const { constants } = require('../constants')

const {
  action_name,
  rasa_server_url,
  sender_id
} = constants

const { vars } = require('../../sergui/vars');

var {
    CHAT_MSG_DELAY_MAX,
    CHAT_MSG_DELAY_MIN,
    gfb_top_k_gui_indexes,
    top_k_annotation_gui_indexes,
    top_k_annotation_feature_indexes,
} = vars;


const {
  showCardsCarousel,
} = require('./cardsCarousel');

const {
  createChart,
  createChartinModal,
} = require('./charts');

const {
  createCollapsible,
} = require('./collapsible');

const {
  renderDropDwon,
} = require('./dropDown');

const {
  renderGUIRankingData,
  renderExampleGUI,
  renderExampleGUIWithFeature,
  renderGUIReqSummaryModal,
  renderFeatureRanking,
  renderGUIRankingDataForAnnotation,
  renderGUIRankingDataForTopKFinalAnnotation,
  renderTopKFeatureRanking,
  renderGUIRankingDataReselect,
} = require('./guiRankingData');

const {
  renderPdfAttachment,
} = require('./pdfAttachment');

const {
  showQuickReplies,
} = require('./quickReplies');

const {
  addSuggestion,
} = require('./suggestionButtons');

/**
 * scroll to the bottom of the chats after new message has been added to chat
 */
const converter = new showdown.Converter();
function scrollToBottomOfResults() {
  const terminalResultsDiv = document.getElementById("chats");
  terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

/**
 * removes the bot typing indicator from the chat screen
 */
function hideBotTyping() {
    $("#botAvatar").remove();
    $(".botTyping").remove();
    // After the processing of the request, enable the input field
    $("#userInput").prop('disabled', false);
    enableGUISelectionButtons();
    enableFeatureGUISelectionButtons();
    enableGUISelectionButtons();
}

/**
 * adds the bot typing indicator from the chat screen
 */
function showBotTyping() {
    const botTyping = '<img class="botAvatar" id="botAvatar" src="/static/lib/img/robot_avatar.png"/><div class="botTyping"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>';
    $(botTyping).appendTo(".chats");
    $(".botTyping").show();
    scrollToBottomOfResults();
    // During the processing of the request, disable the input field
    $("#userInput").prop('disabled', true);
    disableGUISelectionButtons();
    disableFeatureGUISelectionButtons();
    disableGUIReSelectionButtons();
}

/**
 * Set user response on the chat screen
 * @param {String} message user message
 */
function setUserResponse(message) {
  const user_response = `<img class="userAvatar" src='/static/lib/img/userAvatar.jpg'><p class="userMsg">${message} </p><div class="clearfix"></div>`;
  $(user_response).appendTo(".chats").show("slow");

  $(".usrInput").val("");
  scrollToBottomOfResults();
  showBotTyping();
  $(".suggestions").remove();
}

/**
 * returns formatted bot response
 * @param {String} text bot message response's text
 *
 */
function getBotResponse(text) {
  botResponse = `<img class="botAvatar" src="/static/lib/img/robot_avatar.png"/><span class="botMsg">${text}</span><div class="clearfix"></div>`;
  return botResponse;
}

function checkResponseForAction(response) {
  ACTION_FEATURE = "Please briefly name the required feature."
  ACTION_NLR = "Please describe briefly the requirements for your next GUI."
for (var i = 0; i < response.length; i++) {
  if (response[i].hasOwnProperty("text")) {
    if (response[i].text == ACTION_FEATURE || response[i].text == ACTION_NLR) {
        return true;
    }
  }
}
return false;
}

/**
 * renders bot response on to the chat screen
 * @param {Array} response json array containing different types of bot response
 *
 * for more info: `https://rasa.com/docs/rasa/connectors/your-own-website#request-and-response-format`
 */
function setBotResponse(response) {
  hideBotTyping();
  if (response.length < 1) {
    // if there is no response from Rasa, send  fallback message to the user
    const fallbackMsg = "I am facing some issues, please try again later!!!";

    const BotResponse = `<img class="botAvatar" src="/static/lib/img/robot_avatar.png"/><p class="botMsg">${fallbackMsg}</p><div class="clearfix"></div>`;

    $(BotResponse).appendTo(".chats").hide().fadeIn(1000);
    scrollToBottomOfResults();
  } else {
    containsQuickReplies = false;
    addedDelay = 0;
    // if we get response from Rasa
    for (let i = 0; i < response.length; i += 1) {
        //check if the response contains "text"
        if (i != 0 && response[i].hasOwnProperty("text")) { 
            delay = computeTextDelay(response[i].text);
            addedDelay += delay;
        }
        if (Object.hasOwnProperty.call(response[i], "custom")) {
                const { payload } = response[i].custom;
                if (payload === "quickReplies") {
                  containsQuickReplies = true;
                }
            }
        renderBotResponse(response, i, addedDelay);
    }
  }
  setTimeout(function(){
      hideBotTyping();
        //Check if the response is a specfic action, then we need to disable buttons
      if (checkResponseForAction(response)) {
        disableGUISelectionButtons();
        disableFeatureGUISelectionButtons();
      }
      if (containsQuickReplies) {
          $("#userInput").prop('disabled', true);
      } else {
          $("#userInput").prop('disabled', false);
          $("#userInput").focus();
    }
  }, addedDelay)

}

function computeTextDelay(text) {
    let delay = text.length * 30;
      if (delay > CHAT_MSG_DELAY_MAX) delay = CHAT_MSG_DELAY_MAX;
      if (delay < CHAT_MSG_DELAY_MIN) delay = CHAT_MSG_DELAY_MIN;
      return delay;
}

  function enableGUISelectionButtons() {
    var buttons = document.querySelectorAll('button[id^="btn-gui-add"]');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = false;
    }
  }

    function enableGUIReSelectionButtons() {
    var buttons = document.querySelectorAll('button[id^="btn-gui-reselect"]');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = false;
    }
  }

  function disableGUISelectionButtons() {
    var buttons = document.querySelectorAll('button[id^="btn-gui-add"]');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
    }
  }


  function disableGUIReSelectionButtons() {
    var buttons = document.querySelectorAll('button[id^="btn-gui-reselect"]');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
    }
  }

    function enableFeatureGUISelectionButtons() {
    var buttons = document.querySelectorAll('button[id^="btn-select-feature"]');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = false;
    }
  }

    function disableFeatureGUISelectionButtons() {
    var buttons = document.querySelectorAll('button[id^="btn-select-feature"]');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
    }
  }

function renderBotResponse(response, i, addedDelay) {
  setTimeout(function() {
        hideBotTyping();
        // check if the response contains "text"
        if (Object.hasOwnProperty.call(response[i], "text")) {
          if (response[i].text != null) {
            // convert the text to mardown format using showdown.js(https://github.com/showdownjs/showdown);
            let botResponse;
            let html = converter.makeHtml(response[i].text);
            html = html
              .replaceAll("<p>", "")
              .replaceAll("</p>", "")
              .replaceAll("<strong>", "<b>")
              .replaceAll("</strong>", "</b>");
            html = html.replace(/(?:\r\n|\r|\n)/g, "<br>");
            // check for blockquotes
            if (html.includes("<blockquote>")) {
              html = html.replaceAll("<br>", "");
              botResponse = getBotResponse(html);
            }
            // check for image
            if (html.includes("<img")) {
              html = html.replaceAll("<img", '<img class="imgcard_mrkdwn" ');
              botResponse = getBotResponse(html);
            }
            // check for preformatted text
            if (html.includes("<pre") || html.includes("<code>")) {
              botResponse = getBotResponse(html);
            }
            // check for list text
            if (
              html.includes("<ul") ||
              html.includes("<ol") ||
              html.includes("<li") ||
              html.includes("<h3")
            ) {
              html = html.replaceAll("<br>", "");
              // botResponse = `<img class="botAvatar" src="./static/img/sara_avatar.png"/><span class="botMsg">${html}</span><div class="clearfix"></div>`;
              botResponse = getBotResponse(html);
            } else {
              // if no markdown formatting found, render the text as it is.
              if (!botResponse) {
                botResponse = `<img class="botAvatar" src="/static/lib/img/robot_avatar.png"/><p class="botMsg">${response[i].text}</p><div class="clearfix"></div>`;
              }
            }
            // append the bot response on to the chat screen
            $(botResponse).appendTo(".chats").hide().fadeIn(1000);
          }
        }

        // check if the response contains "images"
        if (Object.hasOwnProperty.call(response[i], "image")) {
          if (response[i].image !== null) {
            const BotResponse = `<div class="singleCard"><img class="imgcard" src="${response[i].image}"></div><div class="clearfix">`;

            $(BotResponse).appendTo(".chats").hide().fadeIn(1000);
          }
        }

        // check if the response contains "buttons"
        if (Object.hasOwnProperty.call(response[i], "buttons")) {
          if (response[i].buttons.length > 0) {
            addSuggestion(response[i].buttons);
          }
          scrollToBottomOfResults();
        }

        // check if the response contains "attachment"
        if (Object.hasOwnProperty.call(response[i], "attachment")) {
          if (response[i].attachment != null) {
            if (response[i].attachment.type === "video") {
              // check if the attachment type is "video"
              const video_url = response[i].attachment.payload.src;

              const BotResponse = `<div class="video-container"> <iframe src="${video_url}" frameborder="0" allowfullscreen></iframe> </div>`;
              $(BotResponse).appendTo(".chats").hide().fadeIn(1000);
            }
          }
        }
        // check if the response contains "custom" message
        if (Object.hasOwnProperty.call(response[i], "custom")) {
          const { payload } = response[i].custom;
          if (payload == "gui-ranking") {
             // Check if the custom payload type is "gui-ranking"
             $("#workbench-header").text("GUI Ranking");
             $('#container-workbench').css("background-color", '#e6fff2');
             guiRankingData = response[i].custom.data;
             renderGUIRankingData(guiRankingData);
             scrollToBottomOfResults();
          }
           if (payload == "gui-ranking-reselect") {
             // Check if the custom payload type is "gui-ranking"
             $("#workbench-header").text("GUI Ranking");
             $('#container-workbench').css("background-color", '#e6fff2');
             guiRankingData = response[i].custom.data;
             renderGUIRankingDataReselect(guiRankingData);
             scrollToBottomOfResults();
          }
          if (payload == "gfb") {
             // Check if the custom payload type is "gfb"
             $("#workbench-header").text("GUI Feedback");
             gui_index = response[i].custom.data;
             renderExampleGUI(gui_index);
             scrollToBottomOfResults();
          }
          if (payload == "gfb-top-k") {
             // Check if the custom payload type is "gfb"
             $("#workbench-header").text("GUI Feedback");
             gui_ranking = response[i].custom.data;
             renderGUIRankingDataForAnnotation(gui_ranking);
             scrollToBottomOfResults();
          }
          if (payload == "top-k-rankings-for-annotation") {
             // Check if the custom payload type is "gfb"
             $("#workbench-header").text("GUI Annotation");
             gui_ranking = response[i].custom.data;
             renderGUIRankingDataForTopKFinalAnnotation(gui_ranking);
             scrollToBottomOfResults();
          }
          if (payload == "dfb") {
             // Check if the custom payload type is "dfb"
             $("#workbench-header").text("Feature Feedback");
             $('#container-workbench').css("background-color", '#e6f2ff');
             data = response[i].custom.data;
             renderExampleGUIWithFeature(data);
             scrollToBottomOfResults();
          }
          if (payload == "dfb-top-k") {
             // Check if the custom payload type is "dfb"
             $("#workbench-header").text("Feature Feedback");
             $('#container-workbench').css("background-color", '#e6f2ff');
             data = response[i].custom.data;
             renderFeatureRanking(data);
             scrollToBottomOfResults();
          }
           if (payload == "top-k-feature-rankings-for-annotation") {
             // Check if the custom payload type is "dfb"
             $("#workbench-header").text("Feature Feedback");
             $('#container-workbench').css("background-color", '#e6f2ff');
             data = response[i].custom.data;
             renderTopKFeatureRanking(data);
             scrollToBottomOfResults();
          }
          if (payload == "gui-req-summary") {
             // Check if the custom payload type is "dfb"
             data = response[i].custom.data;
             $("#preview-header").text("Preview");
             $('#selected-gui-wrapper').children().remove();
             renderGUIReqSummaryModal(data);
             scrollToBottomOfResults();
          }
          if (payload === "quickReplies") {
            // check if the custom payload type is "quickReplies"
            const quickRepliesData = response[i].custom.data;
            showQuickReplies(quickRepliesData);
            scrollToBottomOfResults();
            return;
          }

          // check if the custom payload type is "pdf_attachment"
          if (payload === "pdf_attachment") {
            renderPdfAttachment(response[i]);
            scrollToBottomOfResults();
            return;
          }

          // check if the custom payload type is "dropDown"
          if (payload === "dropDown") {
            const dropDownData = response[i].custom.data;
            renderDropDwon(dropDownData);
            addDropDownEventHandler();
            scrollToBottomOfResults();
            return;
          }

          // check if the custom payload type is "cardsCarousel"
          if (payload === "cardsCarousel") {
            const restaurantsData = response[i].custom.data;
            showCardsCarousel(restaurantsData);
            scrollToBottomOfResults();
            return;
          }

          // check if the custom payload type is "chart"
          if (payload === "chart") {
            /**
             * sample format of the charts data:
             *  var chartData =  { "title": "Leaves", "labels": ["Sick Leave", "Casual Leave", "Earned Leave", "Flexi Leave"], "backgroundColor": ["#36a2eb", "#ffcd56", "#ff6384", "#009688", "#c45850"], "chartsData": [5, 10, 22, 3], "chartType": "pie", "displayLegend": "true" }
             */

            const chartData = response[i].custom.data;
            const {
              title,
              labels,
              backgroundColor,
              chartsData,
              chartType,
              displayLegend,
            } = chartData;

            // pass the above variable to createChart function
            createChart(
              title,
              labels,
              backgroundColor,
              chartsData,
              chartType,
              displayLegend
            );

            // on click of expand button, render the chart in the charts modal
            $(document).on("click", "#expand", () => {
              createChartinModal(
                title,
                labels,
                backgroundColor,
                chartsData,
                chartType,
                displayLegend
              );
            });
            scrollToBottomOfResults();
            return;
          }

          // check of the custom payload type is "collapsible"
          if (payload === "collapsible") {
            const { data } = response[i].custom;
            // pass the data variable to createCollapsible function
            createCollapsible(data);
            scrollToBottomOfResults();
          }
        }
      scrollToBottomOfResults();
      showBotTyping();
  }, addedDelay)
}

/**
 * sends the user message to the rasa server,
 * @param {String} message user message
 */
async function send(message) {
  await new Promise((r) => setTimeout(r, 2000));
  $.ajax({
    url: rasa_server_url,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ message, sender: sender_id , csrfmiddlewaretoken:csrftoken }),
    success(botResponse, status) {
      // if user wants to restart the chat and clear the existing chat contents
      if (message.toLowerCase() === "/restart") {
        $("#userInput").prop("disabled", false);

        // if you want the bot to start the conversation after restart
        // customActionTrigger();
        return;
      }
      setBotResponse(botResponse);
    },
    error(xhr, textStatus) {
      if (message.toLowerCase() === "/restart") {
        $("#userInput").prop("disabled", false);
        // if you want the bot to start the conversation after the restart action.
        // actionTrigger();
        // return;
      }

      // if there is no response from rasa server, set error bot response
      setBotResponse("");
    },
  });
}
/**
 * sends an event to the bot,
 *  so that bot can start the conversation by greeting the user
 *
 * `Note: this method will only work in Rasa 1.x`
 */
// eslint-disable-next-line no-unused-vars
function actionTrigger() {
  $.ajax({
    url: `http://localhost:5005/conversations/${sender_id}/execute`,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      name: action_name,
      policy: "MappingPolicy",
      confidence: "0.98",
    }),
    success(botResponse, status) {

      if (Object.hasOwnProperty.call(botResponse, "messages")) {
        setBotResponse(botResponse.messages);
      }
      $("#userInput").prop("disabled", false);
    },
    error(xhr, textStatus) {
      // if there is no response from rasa server
      setBotResponse("");
      $("#userInput").prop("disabled", false);
    },
  });
}

/**
 * sends an event to the custom action server,
 *  so that bot can start the conversation by greeting the user
 *
 * Make sure you run action server using the command
 * `rasa run actions --cors "*"`
 *
 * `Note: this method will only work in Rasa 2.x`
 */
// eslint-disable-next-line no-unused-vars
function customActionTrigger() {
  $.ajax({
    url: "http://localhost:5055/webhook/",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      next_action: action_name,
      tracker: {
        sender_id,
      },
    }),
    success(botResponse, status) {

      if (Object.hasOwnProperty.call(botResponse, "responses")) {
        setBotResponse(botResponse.responses);
      }
      $("#userInput").prop("disabled", false);
    },
    error(xhr, textStatus) {
      // if there is no response from rasa server
      setBotResponse("");
      $("#userInput").prop("disabled", false);
    },
  });
}

/**
 * clears the conversation from the chat screen
 * & sends the `/resart` event to the Rasa server
 */
function restartConversation() {
  $("#userInput").prop("disabled", true);
  // destroy the existing chart
  $(".collapsible").remove();

  if (typeof chatChart !== "undefined") {
    chatChart.destroy();
  }

  $(".chart-container").remove();
  if (typeof modalChart !== "undefined") {
    modalChart.destroy();
  }
  $(".chats").html("");
  $(".usrInput").val("");
  send("/restart");
}
// triggers restartConversation function.
$("#restart").click(() => {
  restartConversation();
});

/**
 * if user hits enter or send button
 * */
$(".usrInput").on("keyup keypress", (e) => {
  const keyCode = e.keyCode || e.which;

  const text = $(".usrInput").val();
  if (keyCode === 13) {
    if (text === "" || $.trim(text) === "") {
      e.preventDefault();
      return false;
    }
    // destroy the existing chart, if yu are not using charts, then comment the below lines
    $(".collapsible").remove();
    $(".dropDownMsg").remove();
    if (typeof chatChart !== "undefined") {
      chatChart.destroy();
    }

    $(".chart-container").remove();
    if (typeof modalChart !== "undefined") {
      modalChart.destroy();
    }

    $("#paginated_cards").remove();
    $(".suggestions").remove();
    $(".quickReplies").remove();
    $(".usrInput").blur();
    setUserResponse(text);
    send(text);
    e.preventDefault();
    return false;
  }
  return true;
});

$("#sendButton").on("click", (e) => {
  const text = $(".usrInput").val();
  if (text === "" || $.trim(text) === "") {
    e.preventDefault();
    return false;
  }
  // destroy the existing chart
  if (typeof chatChart !== "undefined") {
    chatChart.destroy();
  }

  $(".chart-container").remove();
  if (typeof modalChart !== "undefined") {
    modalChart.destroy();
  }

  $(".suggestions").remove();
  $("#paginated_cards").remove();
  $(".quickReplies").remove();
  $(".usrInput").blur();
  $(".dropDownMsg").remove();
  setUserResponse(text);
  send(text);
  e.preventDefault();
  return false;
});

// add event handler if user selects a option.
// eslint-disable-next-line func-names
function addDropDownEventHandler() {
    $("select").on("change", function () {
        let value = "";
        let label = "";
        $("select option:selected").each(() => {
            label += $(this).val();
            value += $(this).val();
        });

        setUserResponse(label);
        // eslint-disable-next-line no-use-before-define
        send(value);
        $(".dropDownMsg").remove();
    });
}

// on click of quickreplies, get the payload value and send it to rasa
$(document).on("click", ".quickReplies .chip", function () {
    const text = this.innerText;
    const payload = this.getAttribute("data-payload");
    setUserResponse(text);
    if (payload == '/finish_gfb_feedback') {
      gfb_feedback = collectGFBFeedback();
      send(`/finish_gfb_feedback{"gfb_feedback":  ${JSON.stringify(gfb_feedback)}}`);
    } else if (payload == '/top_k_gui_annotation_finished') {
      annotation_feedback = collectAnnotationFeedback();
      send(`/top_k_gui_annotation_finished{"annotated_guis":  ${JSON.stringify(annotation_feedback)}}`);
    } else if (payload == '/top_k_feature_annotation_finished') {
      feature_annotation_feedback = collectFeatureAnnotationFeedback();
      send(`/top_k_feature_annotation_finished{"annotated_features":  ${JSON.stringify(feature_annotation_feedback)}}`);
    } else {
      send(payload);
    }

    // delete the quickreplies
    $(".quickReplies").remove();
});

function collectGFBFeedback() {
    var gui_indexes = gfb_top_k_gui_indexes.value;
    gfb_feedback = {}
    for (var i = 0; i < gui_indexes.length; i++) {
          var checkboxVal = $(`input[name='options-outlined-${(i+1)}']:checked`).val();
          if (checkboxVal) {
              gfb_feedback[gui_indexes[i]] = checkboxVal;
          }
    }
    return gfb_feedback;
}

function collectAnnotationFeedback() {
    var gui_indexes = top_k_annotation_gui_indexes.value;
    gfb_feedback = {}
    for (var i = 0; i < gui_indexes.length; i++) {
          var checkboxVal = $(`input[name='options-outlined-${(i+1)}']:checked`).val();
          if (checkboxVal) {
              gfb_feedback[gui_indexes[i]] = checkboxVal;
          }
    }
    return gfb_feedback;
}

function collectFeatureAnnotationFeedback() {
    var gui_indexes = top_k_annotation_feature_indexes.value;
    gfb_feedback = {}
    for (var i = 0; i < gui_indexes.length; i++) {
          var checkboxVal = $(`input[name='options-outlined-${(i+1)}']:checked`).val();
          if (checkboxVal) {
              gfb_feedback[gui_indexes[i]] = checkboxVal;
          }
    }
    return gfb_feedback;
}


// on click of suggestion's button, get the title value and send it to rasa
$(document).on("click", ".menu .menuChips", function () {
    const text = this.innerText;
    const payload = this.getAttribute("data-payload");
    setUserResponse(text);
    send(payload);

    // delete the suggestions once user click on it.
    $(".suggestions").remove();
});


module.exports['send'] = send;
module.exports['scrollToBottomOfResults'] = scrollToBottomOfResults;
module.exports['setUserResponse'] = setUserResponse;
module.exports['showBotTyping'] = showBotTyping;
module.exports['renderBotResponse'] = renderBotResponse;