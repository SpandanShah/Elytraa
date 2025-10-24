// Quiz state
const quizState = {
  currentScreen: "welcome",
  currentQuestion: 1,
  totalQuestions: 6,
  stream: null,
  subjects: [],
  interests: [],
  dreamJob: null,
  feeBudget: null,
  locations: [],
  userInfo: {
    fullName: "",
    score: "",
    email: "",
    mobile: "",
    city: "",
  },
  currentInterestOptions: [],
  currentInterestIndex: 0,
}


document.addEventListener("DOMContentLoaded", () => {
  // Declare Hammer
  var Hammer = window.Hammer

  // Stream-specific options
  const streamOptions = {
    science: {
      subjects: [
        { value: "physics", emoji: "⚛️", label: "Physics" },
        { value: "chemistry", emoji: "🧪", label: "Chemistry" },
        { value: "biology", emoji: "🧬", label: "Biology" },
        { value: "maths", emoji: "🔢", label: "Maths" },
        { value: "computers", emoji: "💻", label: "Computers" },
        { value: "electronics", emoji: "🔌", label: "Electronics" },
      ],
      interests: [
        { value: "building-apps", emoji: "👨‍💻", label: "Building apps" },
        { value: "solving-puzzles", emoji: "🧮", label: "Solving puzzles" },
        { value: "research", emoji: "🔬", label: "Research & discovery" },
        { value: "robotics", emoji: "🤖", label: "Robotics" },
        { value: "space", emoji: "🚀", label: "Space & astronomy" },
        { value: "medicine", emoji: "💊", label: "Medicine & health" },
        { value: "environment", emoji: "🌱", label: "Environment" },
        { value: "still-exploring", emoji: "❓", label: "Still exploring" },
      ],
      jobs: [
        { value: "doctor", emoji: "👨‍⚕️", label: "Doctor" },
        { value: "developer", emoji: "👨‍💻", label: "Software Developer" },
        { value: "engineer", emoji: "👷‍♂️", label: "Engineer" },
        { value: "researcher", emoji: "🔬", label: "Researcher" },
        { value: "data-scientist", emoji: "📊", label: "Data Scientist" },
        { value: "pharmacist", emoji: "💊", label: "Pharmacist" },
        { value: "astronomer", emoji: "🔭", label: "Astronomer" },
        { value: "biotechnologist", emoji: "🧬", label: "Biotechnologist" },
      ],
    },
    commerce: {
      subjects: [
        { value: "accounts", emoji: "📒", label: "Accounts" },
        { value: "economics", emoji: "📈", label: "Economics" },
        { value: "business", emoji: "💼", label: "Business Studies" },
        { value: "maths", emoji: "🔢", label: "Maths" },
        { value: "statistics", emoji: "📊", label: "Statistics" },
        { value: "marketing", emoji: "🛒", label: "Marketing" },
      ],
      interests: [
        { value: "stock-market", emoji: "📈", label: "Stock market" },
        { value: "running-business", emoji: "💼", label: "Running a business" },
        { value: "finance", emoji: "💰", label: "Finance & banking" },
        { value: "marketing", emoji: "📱", label: "Marketing & sales" },
        { value: "economics", emoji: "📊", label: "Economics" },
        { value: "entrepreneurship", emoji: "🚀", label: "Entrepreneurship" },
        { value: "consulting", emoji: "👔", label: "Consulting" },
        { value: "still-exploring", emoji: "❓", label: "Still exploring" },
      ],
      jobs: [
        { value: "ca", emoji: "🧮", label: "Chartered Accountant" },
        { value: "banker", emoji: "🏦", label: "Banker" },
        { value: "financial-analyst", emoji: "📊", label: "Financial Analyst" },
        { value: "marketing-manager", emoji: "📱", label: "Marketing Manager" },
        { value: "entrepreneur", emoji: "🛍️", label: "Entrepreneur" },
        { value: "consultant", emoji: "👔", label: "Management Consultant" },
        { value: "economist", emoji: "📈", label: "Economist" },
        { value: "investment-banker", emoji: "💰", label: "Investment Banker" },
      ],
    },
    arts: {
      subjects: [
        { value: "english", emoji: "💬", label: "English" },
        { value: "history", emoji: "🏛️", label: "History" },
        { value: "geography", emoji: "🌍", label: "Geography" },
        { value: "psychology", emoji: "🧠", label: "Psychology" },
        { value: "sociology", emoji: "👥", label: "Sociology" },
        { value: "political-science", emoji: "🗳️", label: "Political Science" },
        { value: "drawing", emoji: "🖼️", label: "Drawing" },
        { value: "music", emoji: "🎵", label: "Music" },
      ],
      interests: [
        { value: "designing-writing", emoji: "✍️", label: "Designing or writing" },
        { value: "debating-issues", emoji: "👨‍⚖️", label: "Debating issues" },
        { value: "creative-arts", emoji: "🎨", label: "Creative arts" },
        { value: "social-work", emoji: "🤝", label: "Social work" },
        { value: "psychology", emoji: "🧠", label: "Psychology & behavior" },
        { value: "literature", emoji: "📚", label: "Literature" },
        { value: "performing-arts", emoji: "🎭", label: "Performing arts" },
        { value: "still-exploring", emoji: "❓", label: "Still exploring" },
      ],
      jobs: [
        { value: "designer", emoji: "🎨", label: "Graphic Designer" },
        { value: "writer", emoji: "✍️", label: "Writer/Content Creator" },
        { value: "filmmaker", emoji: "🎥", label: "Filmmaker" },
        { value: "teacher", emoji: "🧑‍🏫", label: "Teacher" },
        { value: "lawyer", emoji: "👩‍⚖️", label: "Lawyer" },
        { value: "psychologist", emoji: "🧠", label: "Psychologist" },
        { value: "journalist", emoji: "📰", label: "Journalist" },
        { value: "social-worker", emoji: "🤝", label: "Social Worker" },
      ],
    },
    "not-sure": {
      subjects: [
        { value: "maths", emoji: "🔢", label: "Maths" },
        { value: "english", emoji: "💬", label: "English" },
        { value: "computers", emoji: "💻", label: "Computers" },
        { value: "business", emoji: "📚", label: "Business" },
        { value: "geography", emoji: "🌍", label: "Geography" },
        { value: "drawing", emoji: "🖼️", label: "Drawing" },
        { value: "chemistry", emoji: "🧪", label: "Chemistry" },
        { value: "music", emoji: "🎵", label: "Music" },
      ],
      interests: [
        { value: "building-apps", emoji: "👨‍💻", label: "Building apps" },
        { value: "talking-to-people", emoji: "🎤", label: "Talking to people" },
        { value: "solving-puzzles", emoji: "🧮", label: "Solving puzzles" },
        { value: "designing-writing", emoji: "✍️", label: "Designing or writing" },
        { value: "running-business", emoji: "📈", label: "Running a business" },
        { value: "coming-up-with-ideas", emoji: "💡", label: "Coming up with ideas" },
        { value: "debating-issues", emoji: "👨‍⚖️", label: "Debating issues" },
        { value: "still-exploring", emoji: "❓", label: "Still exploring" },
      ],
      jobs: [
        { value: "doctor", emoji: "👨‍⚕️", label: "Doctor" },
        { value: "developer", emoji: "👨‍💻", label: "Software Developer" },
        { value: "designer", emoji: "🎨", label: "Graphic Designer" },
        { value: "analyst", emoji: "📊", label: "Data Analyst" },
        { value: "filmmaker", emoji: "🎥", label: "Filmmaker" },
        { value: "teacher", emoji: "🧑‍🏫", label: "Teacher" },
        { value: "lawyer", emoji: "👩‍⚖️", label: "Lawyer" },
        { value: "entrepreneur", emoji: "🛍️", label: "Entrepreneur" },
      ],
    },
  }

  // DOM Elements
  const screens = {
    welcome: document.getElementById("welcome-screen"),
    quiz: document.getElementById("quiz-screen"),
    infoForm: document.getElementById("info-form-screen"),
    confirmation: document.getElementById("confirmation-screen"),
    results: document.getElementById("results-screen"),
  }

  const questions = {
    stream: document.getElementById("stream-question"),
    subjects: document.getElementById("subjects-question"),
    interests: document.getElementById("interests-question"),
    dreamJob: document.getElementById("dream-job-question"),
    feeBudget: document.getElementById("fee-budget-question"),
    location: document.getElementById("location-question"),
  }

  const buttons = {
    start: document.getElementById("start-quiz-btn"),
    prev: document.getElementById("prev-btn"),
    next: document.getElementById("next-btn"),
    submit: document.getElementById("submit-form-btn"),
    retake: document.getElementById("retake-btn"),
  }

  const elements = {
    questionCounter: document.getElementById("question-counter"),
    progressBar: document.getElementById("progress-bar"),
    progressPercentage: document.getElementById("progress-percentage"),
    swipeCard: document.getElementById("swipe-card"),
    swipeEmoji: document.querySelector(".swipe-emoji"),
    swipeLabel: document.querySelector(".swipe-label"),
    swipeIndicators: document.querySelector(".swipe-indicators"),
    swipeDoneMessage: document.querySelector(".swipe-done-message"),
    swipeBgLeft: document.querySelector(".swipe-bg-left"),
    swipeBgRight: document.querySelector(".swipe-bg-right"),
    userInfoForm: document.getElementById("user-info-form"),
    resultSummary: document.getElementById("result-summary"),
    recommendationsContainer: document.getElementById("recommendations-container"),
    collegesContainer: document.getElementById("colleges-container"),
    subjectsGrid: document.querySelector("#subjects-question .options-grid"),
    dreamJobGrid: document.querySelector("#dream-job-question .options-grid"),
  }

  // Initialize the quiz
  initializeQuiz()

  // Event Listeners
  buttons.start.addEventListener("click", startQuiz)
  buttons.prev.addEventListener("click", goToPreviousQuestion)
  buttons.next.addEventListener("click", goToNextQuestion)
  buttons.retake.addEventListener("click", retakeQuiz)
  elements.userInfoForm.addEventListener("submit", handleFormSubmit)

  // Initialize stream options
  const streamOptionElements = document.querySelectorAll("#stream-question .option-card")
  streamOptionElements.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      streamOptionElements.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.stream = option.dataset.value

      // Update the subsequent questions based on the selected stream
      updateSubjectsQuestion(quizState.stream)
      updateInterestsQuestion(quizState.stream)
      updateDreamJobQuestion(quizState.stream)

      // Reset selections for subsequent questions
      quizState.subjects = []
      quizState.interests = []
      quizState.dreamJob = null
    })
  })

  // Initialize swipe functionality
  initializeSwipeCard()

  // Initialize fee budget options
  initializeFeeBudgetOptions()

  // Initialize location options
  initializeLocationOptions()

  // Functions
  function initializeQuiz() {
    // Show welcome screen
    showScreen("welcome")

    // Reset quiz state
    quizState.currentQuestion = 1
    quizState.stream = null
    quizState.subjects = []
    quizState.interests = []
    quizState.dreamJob = null
    quizState.feeBudget = null
    quizState.locations = []
    quizState.userInfo = {
      fullName: "",
      score: "",
      email: "",
      mobile: "",
      city: "",
    }
    quizState.currentInterestIndex = 0

    // Update UI
    updateQuestionCounter()
    updateProgressBar()

    // Reset selections
    document.querySelectorAll(".option-card, .option-card-small, .fee-button").forEach((option) => {
      option.classList.remove("selected")
    })

    // Reset form
    elements.userInfoForm.reset()

    // Initialize event listeners for all question options
    initializeFeeBudgetOptions()
    initializeLocationOptions()
  }

  function startQuiz() {
    showScreen("quiz")
    showQuestion(1)
  }

  function showScreen(screenName) {
    // Hide all screens
    Object.values(screens).forEach((screen) => {
      screen.classList.remove("active")
    })

    // Show the requested screen
    screens[screenName].classList.add("active")
    quizState.currentScreen = screenName
  }

  function showQuestion(questionNumber) {
    // Hide all questions
    Object.values(questions).forEach((question) => {
      question.classList.remove("active")
    })

    // Show the requested question
    if (questionNumber === 1) {
      questions.stream.classList.add("active")
    } else if (questionNumber === 2) {
      questions.subjects.classList.add("active")
    } else if (questionNumber === 3) {
      questions.interests.classList.add("active")
      updateSwipeCard()
    } else if (questionNumber === 4) {
      questions.dreamJob.classList.add("active")
    } else if (questionNumber === 5) {
      questions.feeBudget.classList.add("active")
    } else if (questionNumber === 6) {
      questions.location.classList.add("active")
    }

    quizState.currentQuestion = questionNumber
    updateQuestionCounter()
    updateProgressBar()

    // Update button states
    buttons.prev.disabled = questionNumber === 1
    buttons.next.textContent = questionNumber === quizState.totalQuestions ? "Continue" : "Next"
    buttons.next.innerHTML =
      questionNumber === quizState.totalQuestions
        ? 'Continue <i class="fas fa-chevron-right ms-2"></i>'
        : 'Next <i class="fas fa-chevron-right ms-2"></i>'
  }

  function goToPreviousQuestion() {
    if (quizState.currentQuestion > 1) {
      showQuestion(quizState.currentQuestion - 1)
    }
  }

  function goToNextQuestion() {
    if (quizState.currentQuestion < quizState.totalQuestions) {
      showQuestion(quizState.currentQuestion + 1)
    } else {
      // Show the info form after completing all questions
      showScreen("infoForm")
    }
  }

  // function to handle API communication
  async function submitStudentData() {
      const submitBtn = document.getElementById('submit-form-btn');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
      
      // Prepare data for API
      const formData = {
          stream: quizState.stream,
          enjoyed_subjects: quizState.subjects,
          exciting_subjects: quizState.interests,
          dream_job: quizState.dreamJob,
          fees_budget: quizState.feeBudget,
          preferred_locations: quizState.locations,
          name: quizState.userInfo.fullName,
          twelfth_score: quizState.userInfo.score,
          email: quizState.userInfo.email,
          mobile_number: quizState.userInfo.mobile,
          city: quizState.userInfo.city
      };
      
      try {
          const response = await fetch('/api/student/process/', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCSRFToken(),
              },
              body: JSON.stringify(formData)
          });
          
          const data = await response.json();
          
          if (data.success) {
              // Store the API response
              quizState.apiResponse = data.data;
              showResults();
          } else {
              throw new Error(data.error || 'Failed to process your request');
          }
      } catch (error) {
          console.error('Error:', error);
          alert('Sorry, there was an error processing your request. Please try again.');
          showScreen("infoForm");
      } finally {
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Show Me Matching Colleges 🔍';
      }
  }

  // Add CSRF token function
  function getCSRFToken() {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
          const cookies = document.cookie.split(';');
          for (let i = 0; i < cookies.length; i++) {
              const cookie = cookies[i].trim();
              if (cookie.substring(0, 10) === ('csrftoken=')) {
                  cookieValue = decodeURIComponent(cookie.substring(10));
                  break;
              }
          }
      }
      return cookieValue;
  }

  function handleFormSubmit(event) {
    event.preventDefault()

    // Get form data
    quizState.userInfo = {
      fullName: document.getElementById("fullName").value,
      score: document.getElementById("score").value,
      email: document.getElementById("email").value,
      mobile: document.getElementById("mobile").value,
      city: document.getElementById("city").value,
    }

    // Show confirmation screen
    showScreen("confirmation")

    submitStudentData();

    // Simulate loading time
    setTimeout(() => {
      showResults()
    }, 2000)
  }

  function updateQuestionCounter() {
    elements.questionCounter.textContent = `Question ${quizState.currentQuestion}/${quizState.totalQuestions}`
  }

  function updateProgressBar() {
    const progress = (quizState.currentQuestion / quizState.totalQuestions) * 100
    elements.progressBar.style.width = `${progress}%`
    elements.progressBar.setAttribute("aria-valuenow", progress)
    elements.progressPercentage.textContent = `${Math.round(progress)}% Complete`
  }

  function updateSubjectsQuestion(stream) {
    // Clear existing subjects
    elements.subjectsGrid.innerHTML = ""

    // Get subjects for the selected stream
    const subjects = streamOptions[stream || "not-sure"].subjects

    // Create and append subject options
    subjects.forEach((subject) => {
      const subjectElement = document.createElement("div")
      subjectElement.className = "option-card-small"
      subjectElement.dataset.value = subject.value
      subjectElement.innerHTML = `
        <div class="option-emoji">${subject.emoji}</div>
        <div class="option-label">${subject.label}</div>
      `

      // Add click event listener
      subjectElement.addEventListener("click", () => {
        if (subjectElement.classList.contains("selected")) {
          // If already selected, deselect it
          subjectElement.classList.remove("selected")
          quizState.subjects = quizState.subjects.filter((s) => s !== subject.value)
        } else {
          // Select it
          subjectElement.classList.add("selected")
          quizState.subjects.push(subject.value)
        }
      })

      elements.subjectsGrid.appendChild(subjectElement)
    })
  }

  function updateInterestsQuestion(stream) {
    // Get interests for the selected stream
    quizState.currentInterestOptions = streamOptions[stream || "not-sure"].interests
    quizState.currentInterestIndex = 0

    // Reset interests
    quizState.interests = []

    // Initialize swipe indicators
    initializeSwipeIndicators()
  }

  function updateDreamJobQuestion(stream) {
    // Clear existing dream jobs
    elements.dreamJobGrid.innerHTML = ""

    // Get dream jobs for the selected stream
    const jobs = streamOptions[stream || "not-sure"].jobs

    // Create and append job options
    jobs.forEach((job) => {
      const jobElement = document.createElement("div")
      jobElement.className = "option-card-small"
      jobElement.dataset.value = job.value
      jobElement.innerHTML = `
        <div class="option-emoji">${job.emoji}</div>
        <div class="option-label">${job.label}</div>
      `

      // Add click event listener
      jobElement.addEventListener("click", () => {
        // Remove selected class from all options
        document.querySelectorAll("#dream-job-question .option-card-small").forEach((opt) => {
          opt.classList.remove("selected")
        })

        // Add selected class to clicked option
        jobElement.classList.add("selected")

        // Update state
        quizState.dreamJob = job.value
      })

      elements.dreamJobGrid.appendChild(jobElement)
    })
  }

  function initializeSwipeIndicators() {
    // Clear existing indicators
    elements.swipeIndicators.innerHTML = ""

    // Create indicators for each interest option
    quizState.currentInterestOptions.forEach((_, index) => {
      const indicator = document.createElement("div")
      indicator.className = "swipe-indicator"
      if (index === 0) indicator.classList.add("active")
      elements.swipeIndicators.appendChild(indicator)
    })
  }

  function updateSwipeIndicators() {
    const indicators = document.querySelectorAll(".swipe-indicator")
    indicators.forEach((indicator, index) => {
      indicator.classList.remove("active", "completed")
      if (index === quizState.currentInterestIndex) {
        indicator.classList.add("active")
      } else if (index < quizState.currentInterestIndex) {
        indicator.classList.add("completed")
      }
    })
  }

  function initializeSwipeCard() {
    // Initialize Hammer.js for touch gestures
    const hammer = new Hammer(elements.swipeCard)

    hammer.on("pan", (event) => {
      handleSwipe(event)
    })

    hammer.on("panend", (event) => {
      handleSwipeEnd(event)
    })

    // Update the swipe card with the first interest
    updateSwipeCard()
  }

  function updateSwipeCard() {
    if (quizState.currentInterestIndex < quizState.currentInterestOptions.length) {
      const currentInterest = quizState.currentInterestOptions[quizState.currentInterestIndex]
      elements.swipeEmoji.textContent = currentInterest.emoji
      elements.swipeLabel.textContent = currentInterest.label
      elements.swipeCard.style.display = "flex"
      elements.swipeDoneMessage.style.display = "none"
    } else {
      elements.swipeCard.style.display = "none"
      elements.swipeDoneMessage.style.display = "block"
    }

    updateSwipeIndicators()
  }

  function handleSwipe(event) {
    const deltaX = event.deltaX

    // Add swiping class to disable transitions during drag
    elements.swipeCard.classList.add("swiping")

    // Move the card
    elements.swipeCard.style.transform = `translateX(${deltaX}px) rotate(${deltaX * 0.05}deg)`

    // Show background color based on swipe direction
    if (deltaX > 50) {
      elements.swipeBgRight.style.opacity = Math.min(deltaX / 200, 1)
      elements.swipeBgLeft.style.opacity = 0
      elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "1"
      elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "0"
    } else if (deltaX < -50) {
      elements.swipeBgLeft.style.opacity = Math.min(Math.abs(deltaX) / 200, 1)
      elements.swipeBgRight.style.opacity = 0
      elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "1"
      elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "0"
    } else {
      elements.swipeBgLeft.style.opacity = 0
      elements.swipeBgRight.style.opacity = 0
      elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "0"
      elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "0"
    }
  }

  function handleSwipeEnd(event) {
    // Remove swiping class to re-enable transitions
    elements.swipeCard.classList.remove("swiping")

    const deltaX = event.deltaX

    if (deltaX > 100) {
      // Swiped right - like
      const currentInterest = quizState.currentInterestOptions[quizState.currentInterestIndex].value
      if (!quizState.interests.includes(currentInterest)) {
        quizState.interests.push(currentInterest)
      }

      // Animate card off screen to the right
      elements.swipeCard.style.transform = "translateX(1000px) rotate(30deg)"
      setTimeout(() => {
        nextInterest()
      }, 300)
    } else if (deltaX < -100) {
      // Swiped left - dislike
      // Animate card off screen to the left
      elements.swipeCard.style.transform = "translateX(-1000px) rotate(-30deg)"
      setTimeout(() => {
        nextInterest()
      }, 300)
    } else {
      // Reset card position
      elements.swipeCard.style.transform = "translateX(0) rotate(0)"
      elements.swipeBgLeft.style.opacity = 0
      elements.swipeBgRight.style.opacity = 0
      elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "0"
      elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "0"
    }
  }

  function nextInterest() {
    quizState.currentInterestIndex++

    // Reset card position
    elements.swipeCard.style.transform = "translateX(0) rotate(0)"
    elements.swipeBgLeft.style.opacity = 0
    elements.swipeBgRight.style.opacity = 0
    elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "0"
    elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "0"

    // Update the swipe card
    updateSwipeCard()
  }

  function showResults() {
    if (!quizState.apiResponse) {
        alert('No data available. Please try again.');
        showScreen("infoForm");
        return;
    }

    // Generate personalized summary
    const summary = generateSummary()
    elements.resultSummary.textContent = summary

    // Use actual API response for recommendations
    renderRecommendationsFromAPI(quizState.apiResponse.ai_response);

    // Show results screen
    showScreen("results")
  }

  // function to render API recommendations
  function renderRecommendationsFromAPI(apiData) {
      // Parse the API response and extract colleges
      // This will depend on how DeepSeek formats its response
      try {
          const messageContent = apiData.choices[0].message.content;
          const collegesData = JSON.parse(messageContent).colleges;
          
          renderColleges(collegesData);
      } catch (error) {
          console.error('Error parsing API response:', error);
          // Fallback to generated recommendations
          const recommendations = generateRecommendations();
          renderRecommendations(recommendations);
          
          const colleges = generateCollegeRecommendations();
          renderColleges(colleges);
      }
  }

  function retakeQuiz() {
    initializeQuiz()
  }

  function generateSummary() {
    let summary = `Hi ${quizState.userInfo.fullName}, based on your responses, `

    if (quizState.stream === "science") {
      summary += "you have a strong analytical mindset. "
    } else if (quizState.stream === "commerce") {
      summary += "you have a business-oriented perspective. "
    } else if (quizState.stream === "arts") {
      summary += "you have a creative and expressive nature. "
    } else {
      summary += "you're exploring multiple interests. "
    }

    if (quizState.subjects.length > 0) {
      summary += `Your interest in ${getSubjectLabels(quizState.subjects)} shows your academic strengths. `
    }

    if (quizState.dreamJob) {
      summary += `Your aspiration to become a ${getDreamJobLabel(quizState.dreamJob)} aligns well with our recommendations. `
    }

    if (quizState.locations.length > 0) {
      if (quizState.locations.includes("anywhere")) {
        summary += "Your flexibility in location gives you many great options. "
      } else if (quizState.locations.length === 1) {
        summary += `We've focused on options in ${getLocationLabel(quizState.locations[0])}. `
      } else {
        summary += "We've considered your location preferences in our recommendations. "
      }
    }

    return summary
  }

  function getSubjectLabels(subjects) {
    if (subjects.length === 0) return ""
    if (subjects.length === 1) {
      const subject = subjects[0]
      const stream = quizState.stream || "not-sure"
      const subjectObj = streamOptions[stream].subjects.find((s) => s.value === subject)
      return subjectObj ? subjectObj.label.toLowerCase() : subject
    }

    const stream = quizState.stream || "not-sure"
    const subjectLabels = subjects.map((subject) => {
      const subjectObj = streamOptions[stream].subjects.find((s) => s.value === subject)
      return subjectObj ? subjectObj.label.toLowerCase() : subject
    })

    return subjectLabels.slice(0, -1).join(", ") + " and " + subjectLabels[subjectLabels.length - 1]
  }

  function getDreamJobLabel(value) {
    const stream = quizState.stream || "not-sure"
    const job = streamOptions[stream].jobs.find((j) => j.value === value)
    return job ? job.label : value
  }

  function getLocationLabel(value) {
    const labels = {
      mumbai: "Mumbai",
      dehradun: "Dehradun",
      pune: "Pune",
      "my-city": "your current city",
      anywhere: "any location",
    }
    return labels[value] || value
  }

  function generateRecommendations() {
    const recommendations = []
    const stream = quizState.stream || "not-sure"

    // Based on stream and subjects
    if (stream === "science") {
      if (quizState.subjects.includes("computers") || quizState.interests.includes("building-apps")) {
        recommendations.push({ name: "Computer Science", emoji: "💻" })
      }
      if (quizState.subjects.includes("physics") || quizState.subjects.includes("maths")) {
        recommendations.push({ name: "Engineering", emoji: "🔧" })
      }
      if (quizState.subjects.includes("biology") || quizState.dreamJob === "doctor") {
        recommendations.push({ name: "Medicine", emoji: "🏥" })
      }
      if (quizState.subjects.includes("chemistry") && quizState.interests.includes("research")) {
        recommendations.push({ name: "Chemical Engineering", emoji: "⚗️" })
      }
    }

    if (stream === "commerce") {
      if (quizState.subjects.includes("accounts") || quizState.dreamJob === "ca") {
        recommendations.push({ name: "Chartered Accountancy", emoji: "📊" })
      }
      if (quizState.subjects.includes("economics") || quizState.dreamJob === "economist") {
        recommendations.push({ name: "Economics", emoji: "📈" })
      }
      if (quizState.subjects.includes("business") || quizState.dreamJob === "entrepreneur") {
        recommendations.push({ name: "Business Administration", emoji: "💼" })
      }
      if (quizState.subjects.includes("marketing") || quizState.dreamJob === "marketing-manager") {
        recommendations.push({ name: "Marketing", emoji: "📱" })
      }
    }

    if (stream === "arts") {
      if (quizState.subjects.includes("english") || quizState.dreamJob === "writer") {
        recommendations.push({ name: "Mass Communication", emoji: "📝" })
      }
      if (quizState.subjects.includes("drawing") || quizState.dreamJob === "designer") {
        recommendations.push({ name: "Design", emoji: "🎨" })
      }
      if (quizState.subjects.includes("psychology") || quizState.dreamJob === "psychologist") {
        recommendations.push({ name: "Psychology", emoji: "🧠" })
      }
      if (quizState.subjects.includes("political-science") || quizState.dreamJob === "lawyer") {
        recommendations.push({ name: "Law", emoji: "⚖️" })
      }
    }

    // Based on dream job if no recommendations yet
    if (recommendations.length === 0 && quizState.dreamJob) {
      const jobRecommendations = {
        doctor: { name: "Medicine", emoji: "🏥" },
        developer: { name: "Computer Science", emoji: "💻" },
        engineer: { name: "Engineering", emoji: "🔧" },
        researcher: { name: "Research Sciences", emoji: "🔬" },
        "data-scientist": { name: "Data Science", emoji: "📊" },
        ca: { name: "Chartered Accountancy", emoji: "📊" },
        banker: { name: "Banking & Finance", emoji: "🏦" },
        entrepreneur: { name: "Business Administration", emoji: "💼" },
        designer: { name: "Design", emoji: "🎨" },
        filmmaker: { name: "Film Studies", emoji: "🎬" },
        lawyer: { name: "Law", emoji: "⚖️" },
        psychologist: { name: "Psychology", emoji: "🧠" },
      }

      if (jobRecommendations[quizState.dreamJob]) {
        recommendations.push(jobRecommendations[quizState.dreamJob])
      }
    }

    // Ensure we have at least 3 recommendations
    const defaultRecommendations = [
      { name: "Computer Science", emoji: "💻" },
      { name: "Business Administration", emoji: "💼" },
      { name: "Psychology", emoji: "🧠" },
      { name: "Design", emoji: "🎨" },
      { name: "Digital Marketing", emoji: "📱" },
    ]

    while (recommendations.length < 3) {
      const defaultRec = defaultRecommendations.find((rec) => !recommendations.some((r) => r.name === rec.name))
      if (defaultRec) recommendations.push(defaultRec)
    }

    return recommendations.slice(0, 3)
  }

  function renderRecommendations(recommendations) {
    elements.recommendationsContainer.innerHTML = ""

    recommendations.forEach((rec) => {
      const card = document.createElement("div")
      card.className = "recommendation-card"
      card.innerHTML = `
        <div class="d-flex align-items-center">
          <div class="option-emoji me-3">${rec.emoji}</div>
          <div class="option-label">${rec.name}</div>
        </div>
      `
      elements.recommendationsContainer.appendChild(card)
    })
  }

  function generateCollegeRecommendations() {
    // This would typically come from an API based on the user's answers
    // For now, we'll generate some sample colleges based on user preferences
    const allColleges = [
      {
        name: "Mumbai University",
        location: "Mumbai, Maharashtra",
        initial: "MU",
        streams: ["science", "commerce", "arts"],
        feeBudget: ["1l-2l", "2l-3l"],
      },
      {
        name: "IIT Bombay",
        location: "Mumbai, Maharashtra",
        initial: "IB",
        streams: ["science"],
        feeBudget: ["2l-3l", "3l-plus"],
      },
      {
        name: "Symbiosis Pune",
        location: "Pune, Maharashtra",
        initial: "SP",
        streams: ["commerce", "arts"],
        feeBudget: ["2l-3l", "3l-plus"],
      },
      {
        name: "SRCC Delhi",
        location: "Delhi, NCR",
        initial: "SR",
        streams: ["commerce"],
        feeBudget: ["1l-2l", "2l-3l"],
      },
      {
        name: "NID Ahmedabad",
        location: "Ahmedabad, Gujarat",
        initial: "NI",
        streams: ["arts"],
        feeBudget: ["2l-3l", "3l-plus"],
      },
      {
        name: "AIIMS",
        location: "Delhi, NCR",
        initial: "AI",
        streams: ["science"],
        feeBudget: ["2l-3l", "3l-plus"],
      },
      {
        name: "Graphic Era University",
        location: "Dehradun, Uttarakhand",
        initial: "GE",
        streams: ["science", "commerce"],
        feeBudget: ["1l-2l", "50k-1l"],
      },
      {
        name: "FTII Pune",
        location: "Pune, Maharashtra",
        initial: "FT",
        streams: ["arts"],
        feeBudget: ["1l-2l", "2l-3l"],
      },
    ]

    // Filter colleges based on user preferences
    let filteredColleges = [...allColleges]x

    // Filter by stream if specified
    if (quizState.stream && quizState.stream !== "not-sure") {
      filteredColleges = filteredColleges.filter((college) => college.streams.includes(quizState.stream))
    }

    // Filter by fee budget if specified
    if (quizState.feeBudget) {
      filteredColleges = filteredColleges.filter((college) => college.feeBudget.includes(quizState.feeBudget))
    }

    // Filter by location if specified
    if (quizState.locations.length > 0 && !quizState.locations.includes("anywhere")) {
      const locationFilters = quizState.locations.filter((loc) => loc !== "my-city")
      if (locationFilters.length > 0) {
        filteredColleges = filteredColleges.filter((college) =>
          locationFilters.some((loc) => college.location.toLowerCase().includes(loc)),
        )
      }
    }

    // If no colleges match the filters, return some default options
    if (filteredColleges.length === 0) {
      return allColleges.slice(0, 5)
    }

    return filteredColleges.slice(0, 5) // Return top 5 colleges
  }

  // Enhanced college rendering function
  function renderColleges(colleges) {
      elements.collegesContainer.innerHTML = '';
      
      if (!colleges || colleges.length === 0) {
          elements.collegesContainer.innerHTML = `
              <div class="alert alert-info">
                  No colleges found matching your criteria. Try adjusting your preferences.
              </div>
          `;
          return;
      }
      
      colleges.forEach(college => {
          const card = document.createElement('div');
          card.className = 'college-card mb-4';
          card.innerHTML = `
              <div class="card h-100">
                  <div class="card-body">
                      <div class="d-flex justify-content-between align-items-start mb-3">
                          <h5 class="card-title">${college.name || 'College Name'}</h5>
                          <span class="badge bg-primary">${college.location || 'Location'}</span>
                      </div>
                      <p class="card-text">
                          <strong>Courses:</strong> ${college.courses || 'Not specified'}<br>
                          <strong>Fees:</strong> ${college.fees || 'Not specified'}<br>
                          <strong>Placements:</strong> ${college.placements || 'Not specified'}
                      </p>
                      ${college.why_good_fit ? `<p class="card-text"><strong>Why it's a good fit:</strong> ${college.why_good_fit}</p>` : ''}
                  </div>
                  <div class="card-footer bg-transparent">
                      <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                          <button class="btn btn-outline-primary btn-sm">Save</button>
                          <button class="btn btn-primary btn-sm">Apply Now</button>
                      </div>
                  </div>
              </div>
          `;
          elements.collegesContainer.appendChild(card);
      });
  }

  function initializeFeeBudgetOptions() {
    const feeBudgetOptions = document.querySelectorAll("#fee-budget-question .fee-button");
    feeBudgetOptions.forEach((option) => {
      option.addEventListener("click", () => {
        // Remove selected class from all options
        feeBudgetOptions.forEach((opt) => opt.classList.remove("selected"));
        // Add selected class to clicked option
        option.classList.add("selected");
        // Update state
        quizState.feeBudget = option.dataset.value;
      });
    });
  }

  function initializeLocationOptions() {
    const locationOptions = document.querySelectorAll("#location-question .option-card-small")
    locationOptions.forEach((option) => {
      const value = option.dataset.value

      if (option.classList.contains("selected")) {
        // If already selected, deselect it
        option.classList.remove("selected")
        quizState.locations = quizState.locations.filter((location) => location !== value)
      } else {
        // Select it
        option.classList.add("selected")
        quizState.locations.push(value)
      }
    })
  }
})
