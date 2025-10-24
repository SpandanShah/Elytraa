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
  interestOptions: [
    { value: "building-apps", emoji: "👨‍💻", label: "Building apps" },
    { value: "talking-to-people", emoji: "🎤", label: "Talking to people" },
    { value: "solving-puzzles", emoji: "🧮", label: "Solving puzzles" },
    { value: "designing-writing", emoji: "✍️", label: "Designing or writing" },
    { value: "running-business", emoji: "📈", label: "Running a business" },
    { value: "coming-up-with-ideas", emoji: "💡", label: "Coming up with ideas" },
    { value: "debating-issues", emoji: "👨‍⚖️", label: "Debating issues" },
    { value: "still-exploring", emoji: "❓", label: "Still exploring" },
  ],
  currentInterestIndex: 0,
}


document.addEventListener("DOMContentLoaded", () => {
  // Declare Hammer
  var Hammer = window.Hammer

  // Quiz state

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
    userInfoForm: document.getElementById("user-info-form"),
    resultSummary: document.getElementById("result-summary"),
    recommendationsContainer: document.getElementById("recommendations-container"),
    collegesContainer: document.getElementById("colleges-container"),
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
  const streamOptions = document.querySelectorAll("#stream-question .option-card")
  streamOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      streamOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.stream = option.dataset.value
    })
  })

  // Initialize subject options
  const subjectOptions = document.querySelectorAll("#subjects-question .option-card-small")
  subjectOptions.forEach((option) => {
    option.addEventListener("click", () => {
      const value = option.dataset.value

      if (option.classList.contains("selected")) {
        // If already selected, deselect it
        option.classList.remove("selected")
        quizState.subjects = quizState.subjects.filter((subject) => subject !== value)
      } else {
        // Select it
        option.classList.add("selected")
        quizState.subjects.push(value)
      }
    })
  })

  // Initialize dream job options
  const dreamJobOptions = document.querySelectorAll("#dream-job-question .option-card-small")
  dreamJobOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      dreamJobOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.dreamJob = option.dataset.value
    })
  })

  // Initialize fee budget options
  const feeBudgetOptions = document.querySelectorAll("#fee-budget-question .fee-button")
  feeBudgetOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      feeBudgetOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.feeBudget = option.dataset.value
    })
  })

  // Initialize location options
  const locationOptions = document.querySelectorAll("#location-question .option-card-small")
  locationOptions.forEach((option) => {
    option.addEventListener("click", () => {
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
  })

  // Initialize swipe functionality
  initializeSwipeCard()

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

    // Initialize swipe indicators
    initializeSwipeIndicators()
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

  function initializeSwipeIndicators() {
    // Clear existing indicators
    elements.swipeIndicators.innerHTML = ""

    // Create indicators for each interest option
    quizState.interestOptions.forEach((_, index) => {
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
    if (quizState.currentInterestIndex < quizState.interestOptions.length) {
      const currentInterest = quizState.interestOptions[quizState.currentInterestIndex]
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

    // Show indicators based on swipe direction
    if (deltaX > 50) {
      elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "1"
    } else if (deltaX < -50) {
      elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "1"
    } else {
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
      const currentInterest = quizState.interestOptions[quizState.currentInterestIndex].value
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
      elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "0"
      elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "0"
    }
  }

  function nextInterest() {
    quizState.currentInterestIndex++

    // Reset card position
    elements.swipeCard.style.transform = "translateX(0) rotate(0)"
    elements.swipeCard.querySelector(".swipe-indicator-right").style.opacity = "0"
    elements.swipeCard.querySelector(".swipe-indicator-left").style.opacity = "0"

    // Update the swipe card
    updateSwipeCard()
  }

  function showResults() {
    // Generate personalized summary
    const summary = generateSummary()
    elements.resultSummary.textContent = summary

    // Generate course recommendations
    const recommendations = generateRecommendations()
    renderRecommendations(recommendations)

    // Generate college recommendations
    const colleges = generateCollegeRecommendations()
    renderColleges(colleges)

    // Show results screen
    showScreen("results")
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

    if (quizState.subjects.includes("maths") || quizState.subjects.includes("computers")) {
      summary += "You enjoy logical and technical subjects. "
    }

    if (quizState.subjects.includes("english") || quizState.subjects.includes("drawing")) {
      summary += "You have a creative side that enjoys expression. "
    }

    if (quizState.dreamJob) {
      summary += `Your interest in becoming a ${getDreamJobLabel(quizState.dreamJob)} aligns well with our recommendations. `
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

  function getDreamJobLabel(value) {
    const labels = {
      doctor: "Doctor",
      developer: "Software Developer",
      designer: "Graphic Designer",
      analyst: "Data Analyst",
      filmmaker: "Filmmaker",
      teacher: "Teacher",
      lawyer: "Lawyer",
      entrepreneur: "Entrepreneur",
    }
    return labels[value] || value
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

    // Based on stream
    if (quizState.stream === "science") {
      if (quizState.subjects.includes("computers") || quizState.interests.includes("building-apps")) {
        recommendations.push({ name: "Computer Science", emoji: "💻" })
      }
      if (quizState.subjects.includes("maths") || quizState.interests.includes("solving-puzzles")) {
        recommendations.push({ name: "Engineering", emoji: "🔧" })
      }
      if (quizState.dreamJob === "doctor") {
        recommendations.push({ name: "Medicine", emoji: "🏥" })
      }
    }

    if (quizState.stream === "commerce" || quizState.stream === "not-sure") {
      if (quizState.interests.includes("running-business") || quizState.dreamJob === "entrepreneur") {
        recommendations.push({ name: "Business Administration", emoji: "💼" })
      }
      if (quizState.dreamJob === "analyst") {
        recommendations.push({ name: "Data Analytics", emoji: "📊" })
      }
      recommendations.push({ name: "Economics", emoji: "📈" })
    }

    if (quizState.stream === "arts" || quizState.stream === "not-sure") {
      if (quizState.subjects.includes("english") || quizState.interests.includes("designing-writing")) {
        recommendations.push({ name: "Mass Communication", emoji: "📝" })
      }
      if (quizState.dreamJob === "designer") {
        recommendations.push({ name: "Design", emoji: "🎨" })
      }
      if (quizState.dreamJob === "filmmaker") {
        recommendations.push({ name: "Film Studies", emoji: "🎬" })
      }
      if (quizState.dreamJob === "lawyer") {
        recommendations.push({ name: "Law", emoji: "⚖️" })
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
    let filteredColleges = [...allColleges]

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

  function renderColleges(colleges) {
    elements.collegesContainer.innerHTML = ""

    colleges.forEach((college) => {
      const card = document.createElement("div")
      card.className = "college-card"
      card.innerHTML = `
          <div class="college-info">
            <div class="college-logo">${college.initial}</div>
            <div>
              <div class="college-name">${college.name}</div>
              <div class="college-location">${college.location}</div>
            </div>
          </div>
          <button class="apply-button">Apply Now</button>
        `
      elements.collegesContainer.appendChild(card)
    })
  }
})
