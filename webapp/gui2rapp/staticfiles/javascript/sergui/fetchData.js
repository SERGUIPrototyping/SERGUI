const {
  getUICompObjects,
  addGUIToKonva,
  addTransitionToKonva,
} = require('./konvaWireframing');
const { 
   generateID,
   showGUIButtons,
   hideGUIButtons,
   showGUISummaryButton,
 } = require('./helpers');
const { vars } = require('./vars');
var {
  isEditModeOn,
  showUICinPreview,
  currentSelectedComp,
  guiNodes,
  transitions,
  userSetStartNodeId,
  importHelper,
  currentShownGUINode,
  currentGUIReqSummary,
  baseURL
} = vars;

const {
  updateModalAdditionalRequirements,
  updateModalGUINodes,
  renderGUIReqSummaryModal2,
  addKonvaImageAndFeatureForSummaryRendering,
  addAspectGUIsForPDFSummary
} = require('../rasa/components/guiRankingData')


const {
  send,
  showBotTyping
} = require('../rasa/components/chat')

function getDataFromJson(url, callback) {
  return fetch(url)
    .then((res) => res.json())
    .then((jsonData) => callback(readJSON(jsonData)));
}

async function fetchJSONDataFromIndex(
  image,
  index,
  x,
  y,
  editable,
  extended,
  blank
) {
  if (extended || editable) {
    let returnVal = await Promise.all([
      fetch(
        `${baseURL}/combined/${index}.json`
      ).then((response) => response.json()),

      fetch(
        `${baseURL}/semantic_annotations/${index}.json`
      ).then((response) => {
        return response.json();
      }),
      fetch(
        `${baseURL}/combined_extended/${index}.json`
      ).then((response) => {
        return response ? response.json() : null;
      }),
    ]).then((responses) =>
      fetchAllResponses(index, image, responses, x, y, editable, blank)
    );
    return returnVal;
  } else {
    return Promise.all([
      fetch(
        `${baseURL}/combined/${index}.json`
      ).then((response) => response.json()),

      fetch(
        `${baseURL}/semantic_annotations/${index}.json`
      ).then((response) => response.json()),
    ]).then((responses) =>
      fetchAllResponses(index, image, responses, x, y, editable, blank)
    );
  }
}


function fetchAllResponses(
  index,
  image,
  responses,
  x,
  y,
  editable,
  blank = false
) {
  jsonDataCombined = responses[0];
  jsonDataCombinedExtended = responses[2];
  jsonDataSemantic = responses[1];
  uiCompObjects = getUICompObjects(
    jsonDataCombined,
    jsonDataSemantic,
    jsonDataCombinedExtended
  );
  let bgColor = jsonDataCombinedExtended
    ? jsonDataCombinedExtended.bg_color
    : null; 
      guiNode = createGUINode(index, image, uiCompObjects, editable, bgColor, currentGUIReqSummary.value);
      guiNodes.push(guiNode);
      showGUISummaryButton();
      if (guiNodes.length>1) {
        showGUIButtons();
      }
      currentShownGUINode.value = guiNode
      userSetStartNodeId['id'] = guiNode.id
      addGUIToKonva(guiNode);
      addAspectGUIsForPDFSummary(currentGUIReqSummary.value['aspect_guis']);
      $("#container-konva-player").attr('style','border-style:solid;border-color:#22262a;');
}

function getWireframe() {
   return {'gui_nodes': guiNodes.map(gn => gn.id), 'transitions': transitions}
}

function createGUINode(index, image, uiCompObjects, editable, bgColor, summary) {
    return {
        id: 'gui_' + index,
        index: index,
        x: 0,
        y: 0,
        image: image,
        uiCompObjects: uiCompObjects,
        editable: editable,
        customBgColor: bgColor,
        uiCompGroups: null,
        summary: summary,
      };
}


function createTransition(guiNode, currentSelectedComp) {
    return {
        fromGUI: currentSelectedComp.value.getAttr('id'),
        from: currentSelectedComp.value.getAttr('id'),
        to: guiNode.id,
        id: `${currentSelectedComp.value.getAttr('id')}==>${guiNode.id}`,
  };
}

function addGUIToEditor(
  index,
  x = 0,
  y = 0,
  editable = false,
  extended = false,
  blank = false
) {
  var newImg = new Image();
  newImg.onload = function () {
    fetchJSONDataFromIndex(this, index, x, y, editable, extended, blank);
  };
  newImg.src = `${baseURL}/combined/${index}.jpg`;
}

function fetchSearchResults(query, method, qe_method, max_results) {
  return fetch(
    'http://sergui-tool.com/gui2r/v1/retrieval',
    {
      method: 'post',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: query,
        method: method,
        qe_method: qe_method,
        max_results: max_results,
      }),
    }
  )
    .then((res) => res.json())
    .then((res) => appendAllSearchResults(res));
}

function appendAllSearchResults(results) {
  ranked_documents = results['results'];
  searchResultCards = ranked_documents.map((doc) =>
    searchResultCard(doc['index'], doc['rank'], doc['score'])
  );
  $('#container-search-results').append(searchResultCards);
}

function searchResultCard(index, rank, conf) {
  return `<div class="col-lg-4 col-md-6 col-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED" class="card mb-3 box-shadow">
      <p style="font-size:10px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}.</p>
      <img class="card-img-top myImages" id="myImg-${index}" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">
            <button id="btn-gui-add-${index}" data-val="${index}" class="btn btn-success p-0" style="width:100%" type="submit">+</button>
  
          </div>`;
}

module.exports['fetchJSONDataFromIndex'] = fetchJSONDataFromIndex;
module.exports['addGUIToEditor'] = addGUIToEditor;
module.exports['fetchSearchResults'] = fetchSearchResults;
