from utils.db_connection import DatabaseConnection
import random
import numpy as np
from deap import base, creator, tools, algorithms

class MatcherAgentGA:
    """
    Advanced Matcher Agent using Genetic Algorithm
    More sophisticated than simple version
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.students = []
        self.groups = []
        self.min_group_size = 3
        self.max_group_size = 5
        self.compat_matrix = None
        
        # GA parameters
        self.population_size = 50
        self.generations = 100
        self.crossover_prob = 0.7
        self.mutation_prob = 0.2
    
    def fetch_students(self):
        """Same as simple version - fetch all student data"""
        print("\n[Matcher Agent GA] Fetching student data...")
        
        if not self.db.connect():
            print("Error: Could not connect to database")
            return False
        
        query = """
        SELECT id, student_number, first_name, last_name, 
               email, gwa, year_level
        FROM students
        """
        self.students = self.db.fetch_all(query)
        
        if not self.students:
            print("Error: No students found")
            return False
        
        print(f"✓ Found {len(self.students)} students")
        
        # Fetch additional data
        for student in self.students:
            student_id = student['id']
            
            skills_query = "SELECT skill_name, proficiency_level, years_experience FROM technical_skills WHERE student_id = ?"
            student['skills'] = self.db.fetch_all(skills_query, (student_id,))
            
            traits_query = "SELECT openness, conscientiousness, extraversion, agreeableness, neuroticism, learning_style FROM personality_traits WHERE student_id = ?"
            traits = self.db.fetch_one(traits_query, (student_id,))
            student['traits'] = traits if traits else {}
            
            avail_query = "SELECT day_of_week, time_slot, is_available FROM availability WHERE student_id = ? AND is_available = 1"
            student['availability'] = self.db.fetch_all(avail_query, (student_id,))
        
        print(f"✓ Loaded complete profiles")
        return True
    
    def calculate_compatibility(self, student1, student2):
        """Calculate compatibility score between two students"""
        # Skill diversity
        skills1 = set([s['skill_name'] for s in student1['skills']])
        skills2 = set([s['skill_name'] for s in student2['skills']])
        
        if skills1 and skills2:
            total_skills = skills1.union(skills2)
            common_skills = skills1.intersection(skills2)
            overlap_ratio = len(common_skills) / len(total_skills)
            skill_score = 1 - abs(overlap_ratio - 0.5) * 2
        else:
            skill_score = 0.5
        
        # GWA balance
        if student1['gwa'] and student2['gwa']:
            norm_gwa1 = (5.0 - student1['gwa']) / 4.0
            norm_gwa2 = (5.0 - student2['gwa']) / 4.0
            gwa_diff = abs(norm_gwa1 - norm_gwa2)
            
            if 0.2 <= gwa_diff <= 0.5:
                gwa_score = 1.0
            elif gwa_diff < 0.2:
                gwa_score = 0.7
            else:
                gwa_score = 0.6
        else:
            gwa_score = 0.5
        
        # Schedule overlap
        avail1 = set([f"{a['day_of_week']}_{a['time_slot']}" for a in student1['availability']])
        avail2 = set([f"{a['day_of_week']}_{a['time_slot']}" for a in student2['availability']])
        
        if avail1 and avail2:
            common_slots = avail1.intersection(avail2)
            total_possible = len(avail1.union(avail2))
            schedule_score = len(common_slots) / total_possible if total_possible > 0 else 0
        else:
            schedule_score = 0.5
        
        # Personality compatibility
        traits1 = student1['traits']
        traits2 = student2['traits']
        
        if traits1 and traits2:
            consc_diff = abs(traits1.get('conscientiousness', 3) - traits2.get('conscientiousness', 3))
            consc_score = 1 - (consc_diff / 4.0)
            
            agree_avg = (traits1.get('agreeableness', 3) + traits2.get('agreeableness', 3)) / 2
            agree_score = agree_avg / 5.0
            
            extra_diff = abs(traits1.get('extraversion', 3) - traits2.get('extraversion', 3))
            extra_score = extra_diff / 4.0
            
            personality_score = (consc_score * 0.4 + agree_score * 0.4 + extra_score * 0.2)
        else:
            personality_score = 0.5
        
        # Weighted combination
        overall_score = (
            skill_score * 0.30 +
            gwa_score * 0.20 +
            schedule_score * 0.30 +
            personality_score * 0.20
        )
        
        return round(overall_score, 3)
    
    def create_compatibility_matrix(self):
        """Create compatibility matrix"""
        print("\n[Matcher Agent GA] Calculating compatibility matrix...")
        
        n = len(self.students)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                score = self.calculate_compatibility(self.students[i], self.students[j])
                matrix[i][j] = score
                matrix[j][i] = score
        
        self.compat_matrix = matrix
        print(f"✓ Compatibility matrix created ({n}x{n})")
        return matrix
    
    def evaluate_grouping(self, individual, target_size=4):
        """
        Fitness function for GA
        Evaluates how good a grouping solution is
        """
        groups = self.decode_individual(individual, target_size)
        
        total_fitness = 0
        penalty = 0
        
        for group in groups:
            if len(group) < self.min_group_size or len(group) > self.max_group_size:
                penalty += 100  # Heavy penalty for invalid group sizes
            
            # Calculate average compatibility within group
            group_compat = 0
            count = 0
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    group_compat += self.compat_matrix[group[i]][group[j]]
                    count += 1
            
            avg_compat = group_compat / count if count > 0 else 0
            total_fitness += avg_compat
            
            # Bonus for ideal group size
            if len(group) == target_size:
                total_fitness += 0.1
        
        # We want to maximize fitness, so return negative penalty
        return (total_fitness - penalty,)
    
    def decode_individual(self, individual, target_size):
        """
        Convert GA individual (list of numbers) to actual groups
        """
        n = len(self.students)
        groups = []
        current_group = []
        
        for i, gene in enumerate(individual):
            current_group.append(i)
            
            # Start new group based on gene value or if target size reached
            if gene > 0.5 or len(current_group) >= self.max_group_size:
                if len(current_group) >= self.min_group_size:
                    groups.append(current_group)
                    current_group = []
        
        # Add remaining students
        if current_group:
            if len(current_group) >= self.min_group_size:
                groups.append(current_group)
            elif groups:
                # Add to smallest existing group
                smallest = min(groups, key=len)
                smallest.extend(current_group)
        
        return groups
    
    def form_groups_ga(self, target_group_size=4):
        """
        Form groups using Genetic Algorithm
        """
        print(f"\n[Matcher Agent GA] Running genetic algorithm...")
        print(f"Population: {self.population_size}, Generations: {self.generations}")
        
        # Setup DEAP
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        toolbox = base.Toolbox()
        toolbox.register("attr_float", random.random)
        toolbox.register("individual", tools.initRepeat, creator.Individual,
                        toolbox.attr_float, n=len(self.students))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        toolbox.register("evaluate", self.evaluate_grouping, target_size=target_group_size)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Create initial population
        population = toolbox.population(n=self.population_size)
        
        # Run evolution
        print("  Evolving...")
        for gen in range(self.generations):
            # Evaluate fitness
            fitnesses = list(map(toolbox.evaluate, population))
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit
            
            # Select next generation
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))
            
            # Apply crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.crossover_prob:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Apply mutation
            for mutant in offspring:
                if random.random() < self.mutation_prob:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Re-evaluate modified individuals
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            population[:] = offspring
            
            # Print progress every 20 generations
            if (gen + 1) % 20 == 0:
                fits = [ind.fitness.values[0] for ind in population]
                print(f"  Generation {gen + 1}: Best fitness = {max(fits):.3f}")
        
        # Get best solution
        best_individual = tools.selBest(population, 1)[0]
        best_fitness = best_individual.fitness.values[0]
        
        print(f"\n✓ Evolution complete! Best fitness: {best_fitness:.3f}")
        
        # Decode best solution into groups
        best_groups = self.decode_individual(best_individual, target_group_size)
        
        # Convert to format with student details
        groups = []
        for idx, group_indices in enumerate(best_groups, 1):
            members = [self.students[i] for i in group_indices]
            
            # Calculate compatibility
            group_compat = 0
            count = 0
            for i in range(len(group_indices)):
                for j in range(i + 1, len(group_indices)):
                    group_compat += self.compat_matrix[group_indices[i]][group_indices[j]]
                    count += 1
            
            avg_compat = group_compat / count if count > 0 else 0
            
            groups.append({
                'group_num': idx,
                'members': members,
                'compatibility_score': round(avg_compat, 3)
            })
            
            print(f"  Group {idx}: {len(members)} members, compatibility: {avg_compat:.3f}")
        
        self.groups = groups
        print(f"\n✓ Formed {len(groups)} groups using GA")
        return groups
    
    def save_groups_to_database(self):
        """Save formed groups to database"""
        print("\n[Matcher Agent GA] Saving groups to database...")
        
        saved_count = 0
        
        for group in self.groups:
            group_query = """
            INSERT INTO groups (group_name, compatibility_score, status)
            VALUES (?, ?, ?)
            """
            group_name = f"GA Group {group['group_num']}"
            compat_score = group['compatibility_score']
            
            group_id = self.db.insert_and_get_id(
                group_query, 
                (group_name, compat_score, 'Active')
            )
            
            if group_id:
                for idx, member in enumerate(group['members']):
                    member_query = """
                    INSERT INTO group_members (group_id, student_id, role)
                    VALUES (?, ?, ?)
                    """
                    role = 'Leader' if idx == 0 else 'Member'
                    
                    self.db.execute_query(
                        member_query,
                        (group_id, member['id'], role)
                    )
                
                saved_count += 1
        
        print(f"✓ Saved {saved_count} groups to database")
        return saved_count
    
    def run(self, target_group_size=4):
        """Main method to run the GA matcher agent"""
        print("\n" + "=" * 60)
        print("MATCHER AGENT - GENETIC ALGORITHM VERSION")
        print("=" * 60)
        
        try:
            # Step 1: Fetch students
            if not self.fetch_students():
                return False
            
            # Step 2: Create compatibility matrix
            self.create_compatibility_matrix()
            
            # Step 3: Form groups using GA
            groups = self.form_groups_ga(target_group_size)
            
            if not groups:
                print("Error: No groups formed")
                return False
            
            # Step 4: Save to database
            self.save_groups_to_database()
            
            # Step 5: Display summary
            print("\n" + "=" * 60)
            print("GROUP FORMATION SUMMARY (GA)")
            print("=" * 60)
            
            for group in groups:
                print(f"\nGroup {group['group_num']} (Compatibility: {group['compatibility_score']:.3f})")
                for member in group['members']:
                    print(f"   - {member['first_name']} {member['last_name']} (GWA: {member['gwa']})")
            
            avg_compat = sum(g['compatibility_score'] for g in groups) / len(groups)
            print(f"\nAverage Group Compatibility: {avg_compat:.3f}")
            
            print("\n" + "=" * 60)
            print("✓ MATCHER AGENT (GA) COMPLETED SUCCESSFULLY")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\nError in Matcher Agent GA: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.db.disconnect()

# Test the GA agent
if __name__ == "__main__":
    agent = MatcherAgentGA()
    agent.run(target_group_size=4)