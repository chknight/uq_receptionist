/**
 The template of the app.js
 */
/**
 * This sample shows how to create a Lambda function for handling Alexa Skill requests that:
 *
 * - Web service: communicate with an external web service to get events for specified days in history (Wikipedia API)
 * - Pagination: after obtaining a list of events, read a small subset of events and wait for user prompt to read the next subset of events by maintaining session state
 * - Dialog and Session state: Handles two models, both a one-shot ask and tell model, and a multi-turn dialog model.
 * - SSML: Using SSML tags to control how Alexa renders the text-to-speech.
 *
 * Examples:
 * One-shot model:
 * User:  "Alexa, ask History Buff what happened on August thirtieth."
 * Alexa: "For August thirtieth, in 2003, [...] . Wanna go deeper in history?"
 * User: "No."
 * Alexa: "Good bye!"
 *
 * Dialog model:
 * User:  "Alexa, open History Buff"
 * Alexa: "History Buff. What day do you want events for?"
 * User:  "August thirtieth."
 * Alexa: "For August thirtieth, in 2003, [...] . Wanna go deeper in history?"
 * User:  "Yes."
 * Alexa: "In 1995, Bosnian war [...] . Wanna go deeper in history?"
 * User: "No."
 * Alexa: "Good bye!"
 */


// default initialize
/**
 * App ID for the skill
 */
var APP_ID = undefined; //replace with 'amzn1.echo-sdk-ams.app.[your-unique-value-here]';

var https = require('https');
var request = require('request');

/**
 * The AlexaSkill Module that has the AlexaSkill prototype and helper functions
 */
var AlexaSkill = require('./AlexaSkill');



/**
 * HistoryBuffSkill is a child of AlexaSkill.
 * To read more about inheritance in JavaScript, see the link below.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Introduction_to_Object-Oriented_JavaScript#Inheritance
 */
var HistoryBuffSkill = function() {
    AlexaSkill.call(this, APP_ID);
};

// Extend AlexaSkill
HistoryBuffSkill.prototype = Object.create(AlexaSkill.prototype);
HistoryBuffSkill.prototype.constructor = HistoryBuffSkill;

HistoryBuffSkill.prototype.eventHandlers.onSessionStarted = function (sessionStartedRequest, session) {
    console.log("HistoryBuffSkill onSessionStarted requestId: " + sessionStartedRequest.requestId
        + ", sessionId: " + session.sessionId);

    // any session init logic would go here
};

HistoryBuffSkill.prototype.eventHandlers.onLaunch = function (launchRequest, session, response) {
    console.log("HistoryBuffSkill onLaunch requestId: " + launchRequest.requestId + ", sessionId: " + session.sessionId);
    getWelcomeResponse(response);
};

HistoryBuffSkill.prototype.eventHandlers.onSessionEnded = function (sessionEndedRequest, session) {
    console.log("onSessionEnded requestId: " + sessionEndedRequest.requestId
        + ", sessionId: " + session.sessionId);

    // any session cleanup logic would go here
};

HistoryBuffSkill.prototype.intentHandlers = {

    "GeneralEventIntent": function (intent, session, response) {
        handleGeneralEventRequest(intent, session, response);
    },

    "CourseDescriptionIntent": function (intent, session, response) {
        handleCourseDescriptionRequest(intent, session, response);
    },

    "LecturerIntent": function (intent, session, response) {
        handleLecturerRequest(intent, session, response);
    },

    "AMAZON.HelpIntent": function (intent, session, response) {
        var speechText = "With History Buff, you can get historical events for any day of the year.  " +
            "For example, you could say today, or August thirtieth, or you can say exit. Now, which day do you want?";
        var repromptText = "Which day do you want?";
        var speechOutput = {
            speech: speechText,
            type: AlexaSkill.speechOutputType.PLAIN_TEXT
        };
        var repromptOutput = {
            speech: repromptText,
            type: AlexaSkill.speechOutputType.PLAIN_TEXT
        };
        response.ask(speechOutput, repromptOutput);
    },

    "AMAZON.StopIntent": function (intent, session, response) {
        var speechOutput = {
                speech: "No Worries. Goodbye",
                type: AlexaSkill.speechOutputType.PLAIN_TEXT
        };
        response.tell(speechOutput);
    },

    "AMAZON.CancelIntent": function (intent, session, response) {
        var speechOutput = {
                speech: "Goodbye",
                type: AlexaSkill.speechOutputType.PLAIN_TEXT
        };
        response.tell(speechOutput);
    }
};

/**
 * Function to handle the onLaunch skill behavior
 */

function getWelcomeResponse(response) {
    // If we wanted to initialize the session to have some attributes we could add those here.
    var cardTitle = "UQ Fact";
    var repromptText = "With University Expert, you can get anything you want to know.";
    var speechText = "<p>UQ Expert.</p> <p>What can I do for you?</p>";
    var cardOutput = "UQ Expert. What can I do for you?";
    // If the user either does not reply to the welcome message or says something that is not
    // understood, they will be prompted again with this text.

    var speechOutput = {
        speech: "<speak>" + speechText + "</speak>",
        type: AlexaSkill.speechOutputType.SSML
    };
    var repromptOutput = {
        speech: repromptText,
        type: AlexaSkill.speechOutputType.PLAIN_TEXT
    };
    response.askWithCard(speechOutput, repromptOutput, cardTitle, cardOutput);
}

/**
 * Gets a poster prepares the speech to reply to the user.
 */
function handleGeneralEventRequest(intent, session, response) {
    var generalQuery = intent.slots.query;
    var query = generalQuery.value;
    var repromptText = "With University Expert, you can get anything you want to know.";
    var sessionAttributes = {};
    // Read the first 3 events, then set the count to 3
    sessionAttributes.index = paginationSize;
    var date = "";

    // If the user provides a date, then use that, otherwise use today
    // The date is in server time, not in the user's time zone. So "today" for the user may actually be tomorrow
    // if (daySlot && daySlot.value) {
    //     date = new Date(daySlot.value);
    // } else {
    //     date = new Date();
    // }

    var prefixContent = "<p>For " + monthNames[date.getMonth()] + " " + date.getDate() + ", </p>";
    var cardContent = "For " + monthNames[date.getMonth()] + " " + date.getDate() + ", ";

    var cardTitle = "Events on " + monthNames[date.getMonth()] + " " + date.getDate();

    
}

/**
 * Gets a poster prepares the speech to reply to the user.
 */
function handleCourseDescriptionRequest(intent, session, response) {
    var generalQuery = intent.slots.courseName;
    var query = generalQuery.value;
    var target = "description";
    var sessionAttributes = {};
    var repromptText = "With University Expert, you can get anything you want to know.";

    getResultFromServer(target, query, function (events) {
        var speechText = "",
            i;
        var cardTitle = "More events on this day in history";
        var cardContent = "fuck";
        sessionAttributes.text = events;
        session.attributes = sessionAttributes;
        if (events.length == 0) {
            speechText = "There is a problem connecting to Wikipedia at this time. Please try again later.";
            cardContent = speechText;
            response.tell(speechText);
        } else {
            speechText = speechText + "<p>Wanna go deeper in history?</p>";
            var speechOutput = {
                speech: "<speak>" + query + " course talks about " + events + "</speak>",
                // speech: events,
                // type: AlexaSkill.speechOutputType.PLAIN_TEXT
                type: AlexaSkill.speechOutputType.SSML
            };
            var repromptOutput = {
                speech: repromptText,
                type: AlexaSkill.speechOutputType.PLAIN_TEXT
            };
            response.askWithCard(speechOutput, repromptOutput, cardTitle, cardContent);
        }
    });


    // var cardTitle = "More events on this day in history",
    //     sessionAttributes = session.attributes,
    //     result = sessionAttributes.text,
    //     speechText = "",
    //     cardContent = "",
    //     repromptText = "Do you want to know more about what happened on this date?",
    //     i;
    // if (!result) {
    //     speechText = "With History Buff, you can get historical events for any day of the year. For example, you could say today, or August thirtieth. Now, which day do you want?";
    //     cardContent = speechText;
    // } else if (sessionAttributes.index >= result.length) {
    //     speechText = "There are no more events for this date. Try another date by saying <break time = \"0.3s\"/> get events for august thirtieth.";
    //     cardContent = "There are no more events for this date. Try another date by saying, get events for august thirtieth.";
    // } else {
    //     for (i = 0; i < paginationSize; i++) {
    //         if (sessionAttributes.index>= result.length) {
    //             break;
    //         }
    //         speechText = speechText + "<p>" + result[sessionAttributes.index] + "</p> ";
    //         cardContent = cardContent + result[sessionAttributes.index] + " ";
    //         sessionAttributes.index++;
    //     }
    //     if (sessionAttributes.index < result.length) {
    //         speechText = speechText + " Wanna go deeper in history?";
    //         cardContent = cardContent + " Wanna go deeper in history?";
    //     }
    // }
    // var speechOutput = {
    //     speech: "<speak>" + speechText + "</speak>",
    //     type: AlexaSkill.speechOutputType.SSML
    // };
    // var repromptOutput = {
    //     speech: repromptText,
    //     type: AlexaSkill.speechOutputType.PLAIN_TEXT
    // };
    // response.askWithCard(speechOutput, repromptOutput, cardTitle, cardContent);
}

function handleLecturerRequest(intent, session, response) {
    var generalQuery = intent.slots.courseName;
    var query = generalQuery.value;
    var target = "coordinator";
    var sessionAttributes = {};
    var repromptText = "With University Expert, you can get anything you want to know.";

    getResultFromServer(target, query, function (events) {
        var speechText = "",
            i;
        var cardTitle = "More events on this day in history";
        var cardContent = "fuck";
        sessionAttributes.text = events;
        session.attributes = sessionAttributes;
        if (events.length == 0) {
            speechText = "There is a problem connecting to Wikipedia at this time. Please try again later.";
            cardContent = speechText;
            response.tell(speechText);
        } else {
            speechText = speechText + "<p>Wanna go deeper in history?</p>";
            var speechOutput = {
                speech: "<speak>" + events + "</speak>",
                // speech: events,
                // type: AlexaSkill.speechOutputType.PLAIN_TEXT
                type: AlexaSkill.speechOutputType.SSML
            };
            var repromptOutput = {
                speech: repromptText,
                type: AlexaSkill.speechOutputType.PLAIN_TEXT
            };
            response.askWithCard(speechOutput, repromptOutput, cardTitle, cardContent);
        }
    });
}

function getResultFromServer(target, query, eventCallback) {
    var options = {
    url: 'http://104.131.35.172:8888/',
    method: 'POST',
    form: {'name': query, 'target': target}
    };

    // Start the request
    request(options, function (error, response, body) {
        //console.log(body);
        //console.log(error);
        // console.log(body);
        if (!error) {
            // Print out the response body
            //console.log(body)
            eventCallback(body);
        }
    });
}

// Create the handler that responds to the Alexa Request.
exports.handler = function (event, context) {
    // Create an instance of the HistoryBuff Skill.
    var skill = new HistoryBuffSkill();
    skill.execute(event, context);
};

