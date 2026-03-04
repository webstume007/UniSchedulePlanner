import time
from ortools.sat.python import cp_model
from database.crud import get_all_teachers, get_all_rooms, get_all_subjects, get_all_batches, get_global_settings
from datetime import datetime, time as dt_time

class TimetableEngine:
    def __init__(self, db_session, status_callback=None):
        self.session = db_session
        self.status_callback = status_callback
        self.model = cp_model.CpModel()
        self.settings = get_global_settings(db_session)
        
        # Load all department data
        self.teachers = get_all_teachers(db_session)
        self.rooms = get_all_rooms(db_session)
        self.batches = get_all_batches(db_session)
        self.subjects = get_all_subjects(db_session)
        
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        if not self.settings.sunday_off:
            self.days.append("Sunday")
            
        self.open_hour = self.settings.uni_open_time.hour
        self.close_hour = self.settings.uni_close_time.hour
        self.slots = list(range(self.close_hour - self.open_hour))
        
        self.schedule_vars = {}

    def log(self, message, start_time=None):
        if self.status_callback:
            elapsed = f"[{time.time() - start_time:.1f}s] " if start_time else ""
            self.status_callback(f"{elapsed}{message}")

    def generate(self):
        start_time = time.time()
        self.log("🚀 Starting Optimized AI Engine...", start_time)

        # 1. CREATE LESSON LIST
        lessons = []
        for batch in self.batches:
            for subject in batch.curriculum_subjects:
                for part in range(subject.total_credit_hours):
                    lessons.append({
                        "id": f"B{batch.id}_S{subject.id}_P{part}",
                        "batch_id": batch.id,
                        "subject_id": subject.id,
                        "requires_lab": subject.requires_lab,
                        "strength": batch.student_strength
                    })

        self.log(f"🏗️ Pre-calculating slots for {len(lessons)} lessons...", start_time)

        # 2. OPTIMIZED VARIABLE GENERATION (The "Anti-Hang" Logic)
        for lesson in lessons:
            # Pre-filter capable teachers
            cap_teachers = [t.id for t in self.teachers if any(s.id == lesson["subject_id"] for s in t.subjects_can_teach)]
            if not cap_teachers: cap_teachers = [-1]

            # Pre-filter valid rooms
            val_rooms = [(r.id, r.available_from.hour, r.available_to.hour) 
                         for r in self.rooms 
                         if r.capacity >= lesson["strength"] and r.is_lab == lesson["requires_lab"]]
            if not val_rooms: val_rooms = [(-1, 0, 24)]

            for t_id in cap_teachers:
                for r_id, r_from, r_to in val_rooms:
                    for d_idx, day in enumerate(self.days):
                        for slot in self.slots:
                            hour = self.open_hour + slot
                            
                            # Filter out invalid times early
                            if r_id != -1 and (hour < r_from or hour >= r_to): continue
                            if day == "Friday" and hour in [13, 14]: continue

                            v_key = (lesson["id"], t_id, r_id, d_idx, slot)
                            self.schedule_vars[v_key] = self.model.NewBoolVar(f'v{len(self.schedule_vars)}')

        # 3. FAST CONSTRAINT INDEXING
        self.log("⚖️ Enforcing department rules...", start_time)
        
        # Map lessons to variables for faster lookup
        lesson_to_vars = {}
        for (l_id, t_id, r_id, d_idx, slot), var in self.schedule_vars.items():
            lesson_to_vars.setdefault(l_id, []).append(var)

        for l_id, vars_list in lesson_to_vars.items():
            self.model.AddExactlyOne(vars_list)

        # Max Daily Hours Limit
        max_h = getattr(self.settings, 'max_hours_per_day', 2)
        for batch in self.batches:
            for subject in batch.curriculum_subjects:
                for d_idx in range(len(self.days)):
                    daily_vars = [v for k, v in self.schedule_vars.items() 
                                  if k[0].startswith(f"B{batch.id}_S{subject.id}_") and k[3] == d_idx]
                    if daily_vars:
                        self.model.Add(sum(daily_vars) <= max_h)

        # Resource Constraints (Overlap Prevention)
        def add_overlap_constraint(index_pos, entity_list):
            for entity in entity_list:
                for d in range(len(self.days)):
                    for s in self.slots:
                        overlap_vars = [v for k, v in self.schedule_vars.items() 
                                        if k[index_pos] == entity.id and k[3] == d and k[4] == s]
                        if len(overlap_vars) > 1:
                            self.model.AddAtMostOne(overlap_vars)

        add_overlap_constraint(1, self.teachers) # Teacher overlap
        add_overlap_constraint(2, self.rooms)    # Room overlap

        self.log(f"🤖 AI Solving... (Using your 12-Core Hardware)", start_time)

        # 4. EXTREME SOLVER SETTINGS
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15.0 # Circuit breaker
        solver.parameters.num_search_workers = 12    # FULL POWER for your 12-core PC
        
        # Use a strategy that stops as soon as the first feasible table is found
        solver.parameters.search_branching = cp_model.FIXED_SEARCH
        solver.parameters.interleave_search = True 

        status = solver.Solve(self.model)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            self.log("✨ Solution found! Formatting results...", start_time)
            final_schedule = []
            for (l_id, t_id, r_id, d_idx, slot), var in self.schedule_vars.items():
                if solver.Value(var):
                    final_schedule.append({
                        "batch_id": int(l_id.split('_')[0][1:]),
                        "subject_id": int(l_id.split('_')[1][1:]),
                        "teacher_id": t_id,
                        "room_id": r_id,
                        "day": self.days[d_idx],
                        "start_time": f"{self.open_hour + slot:02d}:00",
                        "end_time": f"{self.open_hour + slot + 1:02d}:00"
                    })
            return True, final_schedule
        
        return False, "Timed out. Data is too complex or conflicting. Check teacher workloads."
