const Konva = require('konva');
const { jsPDF } = require("jspdf"); 
const colorThief = new ColorThief();

const {
  fetchJSONDataFromIndex,
  addGUIToEditor,
  fetchSearchResults,
} = require('./fetchData');

const {
  getUICompObjects,
  addGUIToKonva,
  addTransitionToKonva,
} = require('./konvaWireframing');

const {
	send,
	showBotTyping,
  renderBotResponse
} = require('../rasa/components/chat')

const {
  updateModalAdditionalRequirements,
  updateModalGUINodes,
  renderGUIReqSummaryModal2,
  addKonvaImageAndFeatureForSummaryRendering,
} = require('../rasa/components/guiRankingData')


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
  stagePlay,
  guiStack,
  layerPlay,
  currentGUIReqSummary,
  layerAspects,
  stageAspects,
  arrowImg,
  gfb_top_k_gui_indexes,
  baseURL,
} = vars;

const {
  removeUIComponent,
  markUIComponent,
  removeAllTransitionsForGUINode,
  deleteGuiNode,
} = require('./konvaWireframing');

showBotTyping();
send('/intent_start')

$(document).ready(function(){
    var elems = document.querySelectorAll('.modal');
  var instances = M.Modal.init(elems,{
        dismissible:false
      });

    $('.tabs').tabs();
  });

$('#toggle-button').click(function() {
  $('#modal_box').modal('open');
});

let currentShape;
let currentShapeFill;
let currentShapeOpacity;
var menuNode = document.getElementById('menu');

window.addEventListener('click', () => {
  // hide menu
  menuNode.style.display = 'none';
  if (currentShape) {
      currentShape.setAttr('fill', currentShapeFill);
      currentShape.setAttr('opacity', currentShapeOpacity);
      currentShapeFill = undefined;
      currentShapeOpacity = undefined;
      currentShape = null;
  }
  layerPlay.batchDraw();
});

stagePlay.on('contextmenu', function (e) {
  // prevent default behavior
  e.evt.preventDefault();
  if (e.target === stagePlay || e.target.getAttr('id').includes('_back_rec') ||
      e.target.getAttr('id').includes('_action_bar') ||  
      e.target.getAttr('id').includes('_menu') ||  
      e.target.getAttr('id').includes('_back_btn')) {
    // if we are on empty place of the stagePlay we will do nothing or clicked on
    // on the background rectangle
    return;
  }
  if (currentShape) {
      currentShape.setAttr('fill', currentShapeFill);
      currentShape.setAttr('opacity', currentShapeOpacity);
      currentShapeFill = undefined;
      currentShapeOpacity = undefined;
  }
  currentShape = e.target;
  currentShapeFill = currentShape.getAttr('fill');
  currentShapeOpacity = currentShape.getAttr('opacity');
  currentShape.setAttr('fill', 'red');
  currentShape.setAttr('opacity', 0.3);
  var parentNode = currentShape.getParent();
  // show menu
  menuNode.style.display = 'initial';
  var containerRect = $('#container-konva-player').position();
  menuNode.style.top =
     containerRect.top + stagePlay.getPointerPosition().y + 10 + 'px';
  menuNode.style.left =
     containerRect.left + stagePlay.getPointerPosition().x + 4 + 'px';
  layerPlay.batchDraw();
});

$('#workbench-wrapper').on(
  'click',
  'button[id^="btn-gui-add"]',
  function () {
    gui_id = 'gui_' + $(this).data('val');

    $("#preview-header").text("Currently Selected GUI");
    $('#selected-gui-wrapper').append(`
        <img class="card-img-top myImages" style="width:70%;height:70%" id="myImg-${$(this).data('val')}" src=  "${baseURL}/combined/${$(this).data('val')}.jpg" draggable="true" alt="GUI ${$(this).data('val')}">`)


    if(guiNodes.map(n => n.id).includes(gui_id)) {
      alert("The same GUI cannot be added to the preview more than once.");
      return
    }
    renderBotResponse([{'text': 'I am searching for other potentially relevant features for you. Please wait a moment.'}], 0, 0);
    showBotTyping();
    $(".quickReplies").remove();
    send(`/gui_selected{"current_selected_gui_id": "${gui_id}", "current_transition": "None", "current_wireframe": "None"}`);
});

$('#workbench-wrapper').on(
  'click',
  'button[id^="btn-gui-reselect"]',
  function () {
    gui_id = 'gui_' + $(this).data('val');
    if(guiNodes.map(n => n.id).includes(gui_id)) {
      alert("The same GUI cannot be added to the preview more than once.");
      return
    }
    showBotTyping();
    $(".quickReplies").remove();
    send(`/gui_reselected{"current_selected_gui_id": "${gui_id}", "current_transition": "None", "current_wireframe": "None"}`);
});

$('#workbench-wrapper').on(
  'click',
  'button[id^="btn-select-feature"]',
  function () {
    gui_id = 'gui_' + $(this).data('val');
    showBotTyping();
    $(".quickReplies").remove();
    send(`/select_feature{"current_selected_gui_id": "${gui_id}"}`);
});


$('#row-selected-gui-summary').on(
  'click',
  'button[id^="btn-gui-summary"]',
  function () {
    gui_id = 'gui_' + $(this).data('val');
    data = {}
    updateModalAdditionalRequirements(data);
});

$("#gui-previous-button").click(() => {
  currentGUIIndex = guiNodes.map(n => n.id).indexOf(currentShownGUINode.value.id);
  if (!(currentGUIIndex<1)) {
    currentShownGUINode.value = guiNodes[(currentGUIIndex-1)]
    var nextNode = layerPlay.findOne(`#${currentShownGUINode.value.id}`);
    var foundNodes = layerPlay.find(`#${currentShownGUINode.value.id}`)
        var nodeBackButton = layerPlay.findOne(
        `#${nextNode.getAttr('id')}_back_btn`
    );
    nodeBackButton.setAttr('fill', undefined);
    nodeBackButton.setAttr('stroke', undefined);
    nodeBackButton.on('mouseover', function () {
              document.body.style.cursor = 'default';
    });
    guiStack.value = []
    nextNode.moveToTop();
    layerPlay.batchDraw();
  }
});

$("#gui-next-button").click(() => {
  currentGUIIndex = guiNodes.map(n => n.id).indexOf(currentShownGUINode.value.id);
  if (!(currentGUIIndex>= (guiNodes.length-1))) {
    var currentNode = layerPlay.findOne(`#${currentShownGUINode.value.id}`);
    currentNode.moveToBottom();
    currentShownGUINode.value = guiNodes[(currentGUIIndex+1)]
    var nextNode = layerPlay.findOne(`#${currentShownGUINode.value.id}`);
    var nodeBackButton = layerPlay.findOne(
        `#${nextNode.getAttr('id')}_back_btn`
    );
    nodeBackButton.setAttr('fill', undefined);
    nodeBackButton.setAttr('stroke', undefined);
    nodeBackButton.on('mouseover', function () {
                document.body.style.cursor = 'default';
            });
    guiStack.value = []
    nextNode.moveToTop();
    layerPlay.batchDraw();
  }
});

document
  .getElementById('delete-uicomp-button')
  .addEventListener('click', () => {
    removeUIComponent(currentShape);
  });

  document
  .getElementById('btn-pdf')
  .addEventListener('click', () => {
    const doc = new jsPDF({
      orientation: "landscape",
      unit: "mm",
      format: "a4"
    });
    // First we draw the general overview of the app
    createPDFSummaryApp(doc);
    // Second we draw each GUI with its aspect GUIs
    createAspectGUISummaries(doc);
    doc.save('app_summary.pdf'); 
  });


function createPDFSummaryApp(doc) {
    HEADING_FONT_SIZE = 25;
    NORMAL_FONT_SIZE = 15;
    WIDTH = 338;
    HEIGTH = 600.8888;
    if (guiNodes.length > 0) {
       summary = guiNodes[0]['summary'];
       ctx_domain = summary['ctx_domain'];
       ctx_app = summary['ctx_app'];
      doc.setFont(undefined, 'bold').setFontSize(HEADING_FONT_SIZE).text("App Requirements Summary (1)", 10, 21).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE)
    }
    scaling = 0.2;
    y_offset = 45;
    x_offset = 15
    counter = 0;
    pageCount = 1;
    for (var i = 0; i < guiNodes.length; i++) {
      var nextNode = layerPlay.findOne(`#${guiNodes[i]['id']}`);
      nextNode.moveToTop();
      if (counter == 3) {
        counter = 0;
        doc.addPage();
        pageCount = pageCount + 1;
        doc.setFont(undefined, 'bold').setFontSize(HEADING_FONT_SIZE).text("App Requirements Summary ("+pageCount+")", 10, 14).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE)
      }
        doc.addImage(
          stagePlay.toDataURL({ pixelRatio: 2 }),
          (counter*100)+x_offset,
          y_offset,
          stagePlay.width()*scaling*(WIDTH/stagePlay.width()),
          stagePlay.height()*scaling*(HEIGTH/stagePlay.height())
        );
      
      doc.setFont(undefined, 'bold').text("GUI ("+(i+1)+ ")", (counter*100)+x_offset+((stagePlay.width()*scaling)/2)-8, stagePlay.height()*scaling+y_offset+9).setFont(undefined, 'normal');
      if (counter == 1 || counter == 2) {
        doc.addImage(
            arrowImg,
            (counter*100)-7,
            y_offset-11+(stagePlay.height()*scaling)/2,
            arrowImg.width*0.012,
            arrowImg.height*0.012
          );
    }
      counter = counter + 1;
    }
    // reset the preview to the actually shown GUI
    var currentNode = layerPlay.findOne(`#${currentShownGUINode.value.id}`);
    currentNode.moveToTop();
    layerPlay.batchDraw();
}

function createAspectGUISummaries(doc) {
    HEADING_FONT_SIZE = 25;
    MEDIUM_FONTS_IZE = 20;
    NORMAL_FONT_SIZE = 15;
    ASPECT_FONT_SIZE = 11;
    WIDTH = 338;
    HEIGTH = 600.8888;
    scaling_centering = 1.1;
    scaling = 0.2;
    scalingAspect = 0.15;
    y_offset = 45;
    x_offset = 15
    page_counter = 0;
    for (var i = 0; i < guiNodes.length; i++) {
      asp_guis = guiNodes[i]['summary']['aspect_guis'];
      summary = guiNodes[i]['summary']
      nlr = summary['nlr_query']
      if (asp_guis.length>0) {
      page_counter = 0;
      doc.addPage();
      doc.setFont(undefined, 'bold').setFontSize(HEADING_FONT_SIZE).text("GUI ("+(i+1)+") Summary ("+(page_counter+1)+")", 10, 21).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE)
    add_reqs = summary['aspect_guis'].map(e => '"'+e.text+'"').join(', ');
    doc.setFont(undefined, 'bold').text("NL Requirements: ", 10, 32).setFont(undefined, 'normal');
    doc.text('"'+nlr+'"', 57, 32);
      var nextNode = layerPlay.findOne(`#${guiNodes[i]['id']}`);
      nextNode.moveToTop();
      doc.addImage(
          stagePlay.toDataURL({ pixelRatio: 2 }),
          x_offset,
          y_offset,
          stagePlay.width()*scaling*(WIDTH/stagePlay.width()),
          stagePlay.height()*scaling*(HEIGTH/stagePlay.height())
        );
      row_counter = 0;
      col_counter = 0;
      aspect_counter = 0;
      num_guis_left = guiNodes[i]['summary']['aspect_guis'].length;
      NUM_COLS = 3;
      NUM_ASPECTS_PER_PAGE = 6;
      doc.setFont(undefined, 'bold').text("Selected GUI ("+(i+1)+ ")", x_offset+((stagePlay.width()*scaling)/2)-18, stagePlay.height()*scaling+y_offset+9).setFont(undefined, 'normal');
      for (var j = 0; j < guiNodes[i]['summary']['aspect_guis'].length;j++) {
        aspect_gui = guiNodes[i]['summary']['aspect_guis'][j]
        var aspectNode = layerAspects.findOne(`#${aspect_gui['feature_id']}`);
        aspectNode.moveToTop();
             doc.addImage(
                stageAspects.toDataURL({ pixelRatio: 2 }),
                ((col_counter+1)*65)+x_offset+30,
                (row_counter*85)+y_offset-5,
                stageAspects.width()*scalingAspect,
                stageAspects.height()*scalingAspect
          );
        doc.setFont(undefined, 'bold').setFontSize(ASPECT_FONT_SIZE).text('"'+aspect_gui['text']+'"', ((col_counter+1)*65)+x_offset+30+((stageAspects.width()*scalingAspect)/2)-(scaling_centering*aspect_gui['text'].length), stageAspects.height()*scalingAspect+y_offset+1+(row_counter*86)).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE);
        num_guis_left = num_guis_left - 1;
        col_counter = col_counter + 1;
        aspect_counter = aspect_counter + 1;
        if (col_counter>= NUM_COLS) {
          col_counter = 0;
          row_counter = row_counter + 1;
        }
        if (aspect_counter >= NUM_ASPECTS_PER_PAGE && num_guis_left>0) {
                page_counter = page_counter + 1;
                doc.addPage();
                doc.setFont(undefined, 'bold').setFontSize(HEADING_FONT_SIZE).text("GUI ("+(i+1)+") Summary ("+(page_counter+1)+")", 10, 21).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE)
                doc.setFont(undefined, 'bold').text("NL Requirements: ", 10, 32).setFont(undefined, 'normal');
                doc.text('"'+nlr+'"', 57, 32);
                  var nextNode = layerPlay.findOne(`#${guiNodes[i]['id']}`);
                  nextNode.moveToTop();
                  doc.addImage(
                      stagePlay.toDataURL({ pixelRatio: 2 }),
                      x_offset,
                      y_offset,
                      stagePlay.width()*scaling*(WIDTH/stagePlay.width()),
                      stagePlay.height()*scaling*(HEIGTH/stagePlay.height())
                    );
                  doc.setFont(undefined, 'bold').text("Selected GUI ("+(i+1)+ ")", x_offset+((stagePlay.width()*scaling)/2)-18, stagePlay.height()*scaling+y_offset+9).setFont(undefined, 'normal');
            row_counter = 0;
            col_counter = 0;
            aspect_counter = 0;
        }
      }
    }
      // Add new page with additional requirements
      additional_reqs = summary['additional_requirements']// ['password hint and reset', 'password hint', "password hint test et", 'password hint test', 'password hint reset', 'password hint', 'password hint', 'password hint', 'password hint', 'password hint']
      if (additional_reqs.length>0) {
        page_counter = page_counter + 1;
        doc.addPage();
        doc.setFont(undefined, 'bold').setFontSize(HEADING_FONT_SIZE).text("GUI ("+(i+1)+") Summary ("+(page_counter+1)+")", 10, 21).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE)
        doc.setFont(undefined, 'bold').text("NL Requirements: ", 10, 32).setFont(undefined, 'normal');
        doc.text('"'+nlr+'"', 57, 32);
        var nextNode = layerPlay.findOne(`#${guiNodes[i]['id']}`);
        nextNode.moveToTop();
        doc.addImage(
                      stagePlay.toDataURL({ pixelRatio: 2 }),
                      x_offset,
                      y_offset,
                      stagePlay.width()*scaling*(WIDTH/stagePlay.width()),
                      stagePlay.height()*scaling*(HEIGTH/stagePlay.height())
                    );
        doc.setFont(undefined, 'bold').text("Selected GUI ("+(i+1)+ ")", x_offset+((stagePlay.width()*scaling)/2)-18, stagePlay.height()*scaling+y_offset+9).setFont(undefined, 'normal');
        doc.setFont(undefined, 'bold').setFontSize(MEDIUM_FONTS_IZE).text("Additional Requirements", x_offset+3+85, y_offset+10).setFont(undefined, 'normal').setFontSize(NORMAL_FONT_SIZE);
        curr_length = x_offset+85+3;
        MAX_LENGTH = 270;
        curr_y_offset = y_offset+10+10;
        len_factor = 2.7;
        for (var k = 0; k < additional_reqs.length;k++) {
          curr_req = additional_reqs[k];
          if (curr_req.length*len_factor+curr_length>=MAX_LENGTH) {
                  curr_length = (x_offset+85+3);
                  curr_y_offset = curr_y_offset + 9;
                  doc.setFont(undefined, 'bold').text(String(k+1) + '.', curr_length, curr_y_offset).setFont(undefined, 'normal');
                  doc.text(' "'+curr_req+'"', curr_length+(8), curr_y_offset);
                  curr_length += (curr_req.length+6)*len_factor;

          } else {
                doc.setFont(undefined, 'bold').text(String(k+1) + '.', curr_length, curr_y_offset).setFont(undefined, 'normal');
                doc.text(' "'+curr_req+'"', curr_length+(8), curr_y_offset);
                curr_length += (curr_req.length+6)*len_factor;
          }
    }
      }
    }
}

  document
  .getElementById('btn-req-continue')
  .addEventListener('click', () => {
    if (currentGUIReqSummary.value) {
      $('#modal_box').modal('close');
      send(`/gui_selected_confirm`);
      showBotTyping();
      addGUIToEditor(currentGUIReqSummary.value['selected_gui_id'], 0, 0, isEditModeOn.value);
    }
  });

    document
  .getElementById('btn-req-continue-2')
  .addEventListener('click', () => {
      $('#modal_box_app_summary').modal('close');
  });

    document
  .getElementById('btn-req-continue-3')
  .addEventListener('click', () => {
      $('#modal_box_gui_summary').modal('close');
  });

    document
  .getElementById('btn-view-summary')
  .addEventListener('click', () => {
      if (currentShownGUINode.value) {
            renderGUIReqSummaryModal2(currentShownGUINode.value.summary);
      }
  });


    document
  .getElementById('delete-button')
  .addEventListener('click', () => {
    var guiId = currentShape.getParent().getAttr('id');
    var guiNode = guiNodes.find((n) => guiId.includes(n.id));
    deleteGuiNode(currentShape);
    layerPlay.batchDraw();
  });