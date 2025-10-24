# Elytraa
The Billion Dollor

# University Recommendation System – V0.1

This is the backend logic flow for **V0.1** of the University Recommendation System, specifically designed to help undergraduate students in **India** find the best-suited universities based on their preferences and requirements.

---

## 📌 Overview

The system enables students to receive **personalized university recommendations** by filling out a form with key interdependent questions. Based on these inputs, universities are first **filtered**, and then the shortlisted options are **scored and ranked** using a multi-criteria evaluation algorithm.

The system outputs the **Top 10 universities** best suited for the student.

---

## 🧍 Student Sign-Up & Input Phase

The student fills out a form that captures key academic and preference-based criteria. These inputs are used to filter the university dataset.

### Input Fields:
1. **Location (State)** – Preferred state in India
2. **Budget** – Annual tuition budget range
3. **Interest** – Intended course/stream (e.g., B.Tech CSE, BBA, BCom)
4. **Preferred Mode** – Regular or Distance education

These inputs are used to **narrow down the university list** before scoring begins.

---

## 🔍 Filtering Phase

Universities are filtered based on the student's input:
- Must offer the selected **course**
- Must be located in the selected **state**
- Must offer the preferred **mode of education** (regular/distance)
- Must fall within or close to the student's **budget range**

This results in a **shortlist of universities** that satisfy all hard constraints.

---

## 📊 Scoring & Ranking Phase

Once universities are filtered, each one is **scored** using the following structure:

### 🎓 University Score
This measures the overall quality of the university offering the selected course.

#### Components:
| Metric                | Description |
|------------------------|-------------|
| **Infrastructure Score** | Evaluated based on: Quality of labs, Size and location of premises, Availability of sports grounds and equipment |
| **Course Score**        | Detailed evaluation of the specific course offered (see below) |
| **Extra Curricular Score** | Availability of festivals, clubs, workshops, and co-curricular activities |
| **Patent Score**        | Based on the number of patents filed by the university (e.g., 1–3 patents → 10/10 score) |
| **Fees Score**          | Based on how well the university's tuition aligns with the student's budget and scholarship availability |
| **Alumni Score**        | Based on count of notable/successful alumni (e.g., 1–3 alumni → 10/10 score) |

---

### 📘 Course Score
Evaluates the specific **course** the student is interested in.

#### Sub-components:

1. **Faculty Score**
   - Is the faculty permenant, on contract or visiting?
   - Number of research papers published
   - Relevance of research to course topic
   - Patents held by faculty
   - Years of teaching & industry experience
   - Student feedback ratings

2. **Placement Score**
   - Average placement percentage (vs. total batch strength)
   - Median or average package offered

3. **Curriculum Score**
   - Depth and modernity of subjects offered
   - Relevance to current industry needs
   - Availability of electives and specializations

---

### 🧮 Final Score Calculation

Each component above contributes to the final score using predefined weights. A simplified scoring logic:

```

Final Score =
InfraScore \* 15 +
CourseScore \* 30 +
ExtraCurricular \* 10 +
PatentScore \* 10 +
FeesScore \* 15 +
AlumniScore \* 10 +
DegreeScore \* 10

```

Each metric is normalized on a scale of 0–10. The weighted average is then used to **rank the shortlisted universities**, and the **top 10** are returned to the student.

---

## ✅ Output

- **Top 10 Recommended Universities**
- (Optional for later versions) A breakdown of why each university was selected and how it scored on each metric.

---

## 🚧 Notes

- This version focuses only on **backend functionality** and logic.
- No frontend, UI, or responsiveness is part of this scope.
- All calculations are based on **Indian universities only**.
- Future versions may include more user preferences, feedback loops, and advanced explainability features.

---


## 🧠 Future Scope

- Include accreditation score (e.g., NAAC A++)
- Add industry tie-ups and MoUs
- Use real-time placement data APIs
- Feedback loop for refining algorithm accuracy
- Support for PG courses and international universities

---
