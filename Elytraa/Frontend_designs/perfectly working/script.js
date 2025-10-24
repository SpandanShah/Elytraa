const frfr = 'Hello'
// Quiz state
const quizState = {
  currentScreen: "welcome",
  currentQuestion: 1,
  totalQuestions: 10,
  stream: null,
  subjects: [],
  interests: [],
  learningStyle: null,
  dreamPath: null,
  studyLocation: null,
  language: null,
  feeBudget: null,
  relocation: null,
  certainty: null,
  interestOptions: [
    { value: "building-apps", emoji: "👨‍💻", label: "Building apps" },
    { value: "talking-to-people", emoji: "🎤", label: "Talking to people" },
    { value: "solving-puzzles", emoji: "🧮", label: "Solving puzzles" },
    { value: "writing-designing", emoji: "✍️", label: "Writing / designing" },
    { value: "running-business", emoji: "📈", label: "Running a business" },
    { value: "coming-up-with-ideas", emoji: "💡", label: "Coming up with ideas" },
    { value: "debating-issues", emoji: "👨‍⚖️", label: "Debating issues" },
    { value: "still-figuring-out", emoji: "❓", label: "Still figuring it out" },
  ],
  currentInterestIndex: 0,
}

document.addEventListener("DOMContentLoaded", () => {
  // Declare Hammer
  var Hammer = window.Hammer || Hammer

  // Quiz state
  // const quizState = {
  //   currentScreen: "welcome",
  //   currentQuestion: 1,
  //   totalQuestions: 10,
  //   stream: null,
  //   subjects: [],
  //   interests: [],
  //   learningStyle: null,
  //   dreamPath: null,
  //   studyLocation: null,
  //   language: null,
  //   feeBudget: null,
  //   relocation: null,
  //   certainty: null,
  //   interestOptions: [
  //     { value: "building-apps", emoji: "👨‍💻", label: "Building apps" },
  //     { value: "talking-to-people", emoji: "🎤", label: "Talking to people" },
  //     { value: "solving-puzzles", emoji: "🧮", label: "Solving puzzles" },
  //     { value: "writing-designing", emoji: "✍️", label: "Writing / designing" },
  //     { value: "running-business", emoji: "📈", label: "Running a business" },
  //     { value: "coming-up-with-ideas", emoji: "💡", label: "Coming up with ideas" },
  //     { value: "debating-issues", emoji: "👨‍⚖️", label: "Debating issues" },
  //     { value: "still-figuring-out", emoji: "❓", label: "Still figuring it out" },
  //   ],
  //   currentInterestIndex: 0,
  // }

  // DOM Elements
  const screens = {
    welcome: document.getElementById("welcome-screen"),
    quiz: document.getElementById("quiz-screen"),
    results: document.getElementById("results-screen"),
  }

  const questions = {
    stream: document.getElementById("stream-question"),
    subjects: document.getElementById("subjects-question"),
    interests: document.getElementById("interests-question"),
    learningStyle: document.getElementById("learning-style-question"),
    dreamPath: document.getElementById("dream-path-question"),
    studyLocation: document.getElementById("study-location-question"),
    language: document.getElementById("language-question"),
    feeBudget: document.getElementById("fee-budget-question"),
    relocation: document.getElementById("relocation-question"),
    certainty: document.getElementById("certainty-question"),
  }

  const buttons = {
    start: document.getElementById("start-quiz-btn"),
    prev: document.getElementById("prev-btn"),
    next: document.getElementById("next-btn"),
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

  // Initialize stream options
  const streamOptions = document.querySelectorAll("#stream-question .option-card")
  streamOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      streamOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.stream = option.dataset.valueC
      console.log(quizState);
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
        // If not selected and less than 3 subjects are selected, select it
        if (quizState.subjects.length < 3) {
          option.classList.add("selected")
          quizState.subjects.push(value)
        }
      }
    })
  })

  // Initialize learning style options
  const learningStyleOptions = document.querySelectorAll("#learning-style-question .toggle-option")
  learningStyleOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      learningStyleOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.learningStyle = option.dataset.value
    })
  })

  // Initialize dream path options
  const dreamPathOptions = document.querySelectorAll("#dream-path-question .option-card-small")
  dreamPathOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      dreamPathOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.dreamPath = option.dataset.value
    })
  })

  // Initialize study location options
  const studyLocationOptions = document.querySelectorAll("#study-location-question .location-card")
  studyLocationOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      studyLocationOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.studyLocation = option.dataset.value
    })
  })

  // Initialize language options
  const languageOptions = document.querySelectorAll("#language-question .language-button")
  languageOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      languageOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.language = option.dataset.value
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

  // Initialize relocation options
  const relocationOptions = document.querySelectorAll("#relocation-question .relocation-option")
  relocationOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      relocationOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.relocation = option.dataset.value
    })
  })

  // Initialize certainty options
  const certaintyOptions = document.querySelectorAll("#certainty-question .certainty-option")
  certaintyOptions.forEach((option) => {
    option.addEventListener("click", () => {
      // Remove selected class from all options
      certaintyOptions.forEach((opt) => opt.classList.remove("selected"))
      // Add selected class to clicked option
      option.classList.add("selected")
      // Update state
      quizState.certainty = option.dataset.value
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
    quizState.learningStyle = null
    quizState.dreamPath = null
    quizState.studyLocation = null
    quizState.language = null
    quizState.feeBudget = null
    quizState.relocation = null
    quizState.certainty = null
    quizState.currentInterestIndex = 0

    // Update UI
    updateQuestionCounter()
    updateProgressBar()

    // Reset selections
    document
      .querySelectorAll(".option-card, .option-card-small, .toggle-option, .location-card, .language-button, .fee-button, .relocation-option, .certainty-option",)
      .forEach((option) => {
        option.classList.remove("selected")
      })

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
      questions.learningStyle.classList.add("active")
    } else if (questionNumber === 5) {
      questions.dreamPath.classList.add("active")
    } else if (questionNumber === 6) {
      questions.studyLocation.classList.add("active")
    } else if (questionNumber === 7) {
      questions.language.classList.add("active")
    } else if (questionNumber === 8) {
      questions.feeBudget.classList.add("active")
    } else if (questionNumber === 9) {
      questions.relocation.classList.add("active")
    } else if (questionNumber === 10) {
      questions.certainty.classList.add("active")
    }

    quizState.currentQuestion = questionNumber
    updateQuestionCounter()
    updateProgressBar()

    // Update button states
    buttons.prev.disabled = questionNumber === 1
    buttons.next.textContent = questionNumber === quizState.totalQuestions ? "See Results" : "Next"
    buttons.next.innerHTML =
      questionNumber === quizState.totalQuestions
        ? 'See Results <i class="fas fa-chevron-right ms-2"></i>'
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
      showResults()
    }
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
    let summary = "Based on your responses, "

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

    if (quizState.learningStyle === "practical-hands-on") {
      summary += "You learn best through hands-on experiences. "
    } else if (quizState.learningStyle === "theory-reading") {
      summary += "You prefer deep theoretical understanding. "
    }

    if (quizState.certainty === "no-clue" || quizState.certainty === "kinda-lost") {
      summary +=
        "While you're still exploring options, we've found some great matches based on your interests and preferences."
    } else if (quizState.certainty === "very-sure") {
      summary += "You seem confident in your direction, and our recommendations align with your chosen path."
    }

    return summary
  }

  function generateRecommendations() {
    const recommendations = []

    if (quizState.stream === "science") {
      if (quizState.subjects.includes("computers") || quizState.interests.includes("building-apps")) {
        recommendations.push({ name: "Computer Science", emoji: "💻" })
      }
      if (quizState.subjects.includes("maths") || quizState.interests.includes("solving-puzzles")) {
        recommendations.push({ name: "Engineering", emoji: "🔧" })
      }
      recommendations.push({ name: "Data Science", emoji: "📊" })
    }

    if (quizState.stream === "commerce" || quizState.stream === "not-sure") {
      if (quizState.interests.includes("running-business")) {
        recommendations.push({ name: "Business Administration", emoji: "💼" })
      }
      recommendations.push({ name: "Economics", emoji: "📈" })
      recommendations.push({ name: "Digital Marketing", emoji: "📱" })
    }

    if (quizState.stream === "arts" || quizState.stream === "not-sure") {
      if (quizState.subjects.includes("english") || quizState.interests.includes("writing-designing")) {
        recommendations.push({ name: "Mass Communication", emoji: "📝" })
      }
      recommendations.push({ name: "Design", emoji: "🎨" })
      recommendations.push({ name: "Psychology", emoji: "🧠" })
    }

    // Add recommendations based on dream path
    if (quizState.dreamPath === "tech-engineering") {
      recommendations.push({ name: "Computer Engineering", emoji: "🖥️" })
    } else if (quizState.dreamPath === "business-management") {
      recommendations.push({ name: "MBA", emoji: "📊" })
    } else if (quizState.dreamPath === "design-creative") {
      recommendations.push({ name: "UX/UI Design", emoji: "🎨" })
    } else if (quizState.dreamPath === "law-civil-services") {
      recommendations.push({ name: "Law", emoji: "⚖️" })
    } else if (quizState.dreamPath === "medicine-healthcare") {
      recommendations.push({ name: "Medicine", emoji: "🏥" })
    } else if (quizState.dreamPath === "media-entertainment") {
      recommendations.push({ name: "Media Studies", emoji: "🎬" })
    }

    // Ensure we have at least 3 recommendations
    const defaultRecommendations = [
      { name: "Computer Science", emoji: "💻" },
      { name: "Business Administration", emoji: "💼" },
      { name: "Psychology", emoji: "🧠" },
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
    // For now, we'll generate some sample colleges
    const colleges = [
      {
        name: "Tech University",
        location: "Mumbai, Maharashtra",
        initial: "TU",
      },
      {
        name: "Creative Arts College",
        location: "Bangalore, Karnataka",
        initial: "CA",
      },
      {
        name: "Business School of Excellence",
        location: "Delhi, NCR",
        initial: "BS",
      },
      {
        name: "National Institute of Design",
        location: "Ahmedabad, Gujarat",
        initial: "NI",
      },
      {
        name: "Medical Sciences University",
        location: "Chennai, Tamil Nadu",
        initial: "MS",
      },
    ]

    // Filter colleges based on user preferences
    let filteredColleges = [...colleges]

    // Filter by location preference if specified
    if (quizState.studyLocation === "big-city") {
      filteredColleges = filteredColleges.filter((college) =>
        ["Mumbai", "Delhi", "Bangalore", "Chennai"].some((city) => college.location.includes(city)),
      )
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
