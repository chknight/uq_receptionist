GeneralEventIntent {expert|query} using LITERAL

CourseDescriptionIntent tell me something about {courseName}
CourseDescriptionIntent tell me about {courseName}
CourseDescriptionIntent what is the course description of {courseName}
CourseDescriptionIntent what is the course description for {courseName}
CourseDescriptionIntent may I know the information of {courseName}
CourseDescriptionIntent what is the course {courseName}
CourseDescriptionIntent
CourseDescriptionIntent course description of {courseName}
CourseDescriptionIntent course description for {courseName}

UnClassifiedIntent what is the {parameter}
UnClassifiedIntent what about the {parameter}
UnClassifiedIntent

LecturerIntent who is the lecturerof {courseName}
LecturerIntent who is the lecturer for {courseName}
LecturerIntent who teach {courseName}

AssignmentIntent what is the assignment of {courseName}


AMAZON.StopIntent thanks
AMAZON.StopIntent thank you

{
  "intents": [
    {
      "intent": "GeneralEventIntent",
      "slots": [
        {
          "name": "query",
          "type": "LITERAL"
        }
      ]
    },
    {
      "intent": "CourseDescriptionIntent",
      "slots": [
        {
          "name": "courseName",
          "type": "COURSE"
        }
      ]
    },
    {
      "intent": "LecturerIntent",
      "slots": [
        {
          "name": "courseName",
          "type": "COURSE"
        }
      ]
    },
    {
      "intent": "AMAZON.HelpIntent"
    },
    {
      "intent": "AMAZON.StopIntent"
    },
    {
      "intent": "AMAZON.CancelIntent"
    }
  ]
}