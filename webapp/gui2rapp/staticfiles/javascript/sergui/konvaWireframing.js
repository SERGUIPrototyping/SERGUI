const {JSONPath} = require('jsonpath-plus');

const { vars } = require('./vars');
var {
  showUICinPreview,
  isEditModeOn,
  width,
  height,
  currentSelectedComp,
  guiNodes,
  transitions,
  blockSnapSize,
  userSetStartNodeId,
  guiStack,
  importHelper,
  stagePlay,
  layerPlay,
  currentShownGUINode,
  MAX_PLAYER_SCALE,
  scalePlayer,
} = vars;

const {
  getLabelCrop,
  getButtonCrop,
  getInputCrop,
  createCustomButton,
  createCustomInput,
  createCustomLabel,
} = require('./createCustomComps');

const {
  rgbToHex,
  modeI,
  haveIntersection,
  getArrowPoints2,
  getNextId,
  generateID,
  showGUIButtons,
  hideGUIButtons,
  hideGUISummaryButton
} = require('./helpers');

const colorThief = new ColorThief();

function computeScaling(width) {
    const WIDTH_CORRECTION = 110;
    konvaWrapperWidth = $('#konva-player-wrapper').width()
    konvaWrapperHeight = $('#konva-player-wrapper').height();
    return (konvaWrapperWidth-WIDTH_CORRECTION) / width;
}


function createWireframingPlayer2() {  
// Create a new Konva group for each of the guinodes
   for (j = 0; j < guiNodes.length; j++) {
    guiNode = guiNodes[j];
    // Create the Konva Group to capture all Konva objects for this GUI
    var groupPlay = new Konva.Group({name: guiNode.id, id: guiNode.id,});
    // Create the Konva image to visualize the GUI screenshot
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: guiNode.image,
      width: guiNode.image.width * (540 / guiNode.image.width),
      height: guiNode.image.height * (540 / guiNode.image.width),
      id: guiNode.id + '_img', name: guiNode.id + '_img',
    });
    // Update the width and height of the konva objects
    var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
    var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');
    // Compute the scaling factor to obtain adapted konva sizes
    var scalePlayerContainer;
    if (scalePlayer.value) {
        scalePlayerContainer = scalePlayer.value;
    } else {
        scalePlayerContainer = computeScaling(realWidth);
        scalePlayer.value = scalePlayerContainer;
    }
    // Update the width and height using the scaling factor
    var updatedWidth = realWidth * scalePlayerContainer
    var updatedHeight = realHeight * scalePlayerContainer
    imgNodePlay.width(updatedWidth);
    imgNodePlay.height(updatedHeight);
    stagePlay.width(updatedWidth);
    stagePlay.height(updatedHeight);
    // Set the width and height of the actual HTML container with the updated sizes
    $('#container-konva-player').width(updatedWidth).height(updatedHeight);

    // Create a konva group  and related objects for each ui comp
    for (let i = 0; i < guiNode.uiCompObjects.length; i++) {
  	  
      // Current ui comp object
      currUICompObject = guiNode.uiCompObjects[i];
      comp_bounds = currUICompObject['comp_bounds'];
      comp_label = currUICompObject['comp_label'];
      // Scale the bounds of the ui comp using the scaling factor
      let a = comp_bounds;
      let factor = (1440 / guiNode.image.width) * (guiNode.image.width / 540) * (1 / scalePlayerContainer);
      normalizedA = a.map(function (x) {
        return x / factor;
      });
      let width = normalizedA[2] - normalizedA[0];
      let height = normalizedA[3] - normalizedA[1];
      // Set stroke color depending on type and if set
      if (showUICinPreview.value) {
        stroke_color = component_color_mapping[comp_label] || 'black';
      } else {
        stroke_color = undefined;
      }

      // Create the bounding box konva rect for the ui comp object
      var name = currUICompObject.id;
      name = `${guiNode.id}_${i}`;
      var box2Play = new Konva.Rect({x: normalizedA[0], y: normalizedA[1], width: width, height: height,
          stroke_ori: stroke_color, stroke: stroke_color, strokeWidth: 2, opacity: 0.2, id: name, name: name});
      groupPlay.add(box2Play);
      addBox2PlayEventHandlers(box2Play);
    }
  // To each GUI add back button and add the GUI group to the layer
  addBackButton(layerPlay, groupPlay, guiNode, scalePlayerContainer);
  groupPlay.add(imgNodePlay);
  imgNodePlay.setZIndex(0);
  layerPlay.add(groupPlay);
  }
// Add the layer to the konva stage
stagePlay.add(layerPlay);
// Set the start node of the GUI preview player
if (!jQuery.isEmptyObject(userSetStartNodeId)) {
	   var startNode = layerPlay.findOne(`#${userSetStartNodeId.id}`);
	   layerPlay.children.forEach((c) => {console.log(c.getAttr('id'))});
		if (startNode) {
		  startNode.moveToTop();
  	 	}
  	} 
  // Redraw entire Konva player again
  layerPlay.batchDraw();
}

function getBackgroundRectangle(guiNode, imgNodePlay) {
    var detectedColor = colorThief.getColor(guiNode.image);
    var detextedHexColor = rgbToHex(
        detectedColor[0],
        detectedColor[1],
        detectedColor[2]
    );
    var backRect1 = new Konva.Rect({
        x: imgNodePlay.x(),
        y: imgNodePlay.y(),
        width: imgNodePlay.width(),
        height: imgNodePlay.height(),
        fill: !guiNode.blank ? detextedHexColor : '#ffffff',
        opacity: 1,
        id: guiNode.id + '_back_rec',
        name: guiNode.id + '_back_rec',
    });
    if (guiNode.customBgColor && !guiNode.blank) {
      backRect1.setAttr('fill', guiNode.customBgColor);
    }
    return backRect1;
}


function getCroppedComponent(
  darthNode,
  image,
  x1,
  y1,
  width1,
  height1,
  x2,
  y2,
  width2,
  height2,
  draggable
) {
  var imgNodeClone = darthNode.clone();
  imgNodeClone.setAttr('draggable', draggable);

  imgNodeClone.setAttr('x', x1);
  imgNodeClone.setAttr('y', y1);
  imgNodeClone.setAttr('width', width1);
  imgNodeClone.setAttr('height', height1);

  var crop = imgNodeClone.crop({
    x: x2,
    y: y2,
    width: width2, 
    height: height2,
  });
  return crop;
}

function addGUIToKonva(guiNode) {

    var scalingPlayer = 1.0;
    var scaling_factor = 1.0;
    // Create the Konva Group to capture all Konva objects for this GUI
    var groupPlay = new Konva.Group({name: guiNode.id, id: guiNode.id, master: true});
    // Create the Konva image to visualize the GUI screenshot
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: guiNode.image,
      width: guiNode.image.width * (540 / guiNode.image.width),
      height: guiNode.image.height * (540 / guiNode.image.width),
      id: guiNode.id + '_img', name: guiNode.id + '_img',
    });

    // Update the width and height of the konva objects
    var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
    var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');
    // Compute the scaling factor to obtain adapted konva sizes
    var scalePlayerContainer;
    if (scalePlayer.value) {
        scalePlayerContainer = scalePlayer.value;
    } else {
        scalePlayerContainer = computeScaling(realWidth);
        if (scalePlayerContainer >= MAX_PLAYER_SCALE) {
            scalePlayerContainer = MAX_PLAYER_SCALE;
        }
        scalePlayer.value = scalePlayerContainer;
    }
    // Update the width and height using the scaling factor
    var updatedWidth = realWidth * scalePlayerContainer
    var updatedHeight = realHeight * scalePlayerContainer
    imgNodePlay.width(updatedWidth);
    imgNodePlay.height(updatedHeight);
    stagePlay.width(updatedWidth);
    stagePlay.height(updatedHeight);
    // Set the width and height of the actual HTML container with the updated sizes
    $('#container-konva-player').width(updatedWidth).height(updatedHeight);

    // First add the background replacing rectangle
    backRect1 = getBackgroundRectangle(guiNode, imgNodePlay);
    groupPlay.add(backRect1);

      // Second include the action bar
      let factor =
        (1440 / guiNode.image.width) *
        (1 / scaling_factor) *
        (guiNode.image.width / 540) *
        (1 / scalePlayerContainer);
      var abarloc = [0, 0, 1440, 84].map(function (x) {
        return x / factor;
      });
      var abarwidth = abarloc[2] - abarloc[0];
      var abarheight = abarloc[3] - abarloc[1];
      var croppedActionBar = getCroppedComponent(
        imgNodePlay,
        guiNode.image,
        abarloc[0],
        abarloc[1],
        abarwidth,
        abarheight,
        abarloc[0] *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        abarloc[1] *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        abarwidth *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        abarheight *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        false
      );

      croppedActionBar.setAttr('comp_label', 'action_bar');
      croppedActionBar.setAttr('name', guiNode.id + '_action_bar');
      croppedActionBar.setAttr('id', guiNode.id + '_action_bar');
      groupPlay.add(croppedActionBar);
      croppedActionBar.moveToTop();
      croppedActionBar.on('mousedown', function () {
      });
      // Third include the menu bar
      var menuloc = [0, 2393, 1440, 2560].map(function (x) {
        return x / factor;
      });
      var menuwidth = menuloc[2] - menuloc[0];
      var menuheight = menuloc[3] - menuloc[1];
      var cropppedMenu = getCroppedComponent(
        imgNodePlay,
        guiNode.image,
        menuloc[0],
        menuloc[1],
        menuwidth,
        menuheight,
        menuloc[0] *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        menuloc[1] *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        menuwidth *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        menuheight *
          (1 / scaling_factor) *
          (guiNode.image.width / 540) *
          (1 / scalePlayerContainer),
        false
      );

      cropppedMenu.setAttr('comp_label', 'menu');
      cropppedMenu.setAttr('name', guiNode.id + '_menu');
      cropppedMenu.setAttr('id', guiNode.id + '_menu');
      groupPlay.add(cropppedMenu);
      imgNodePlay.visible(false);
      groupPlay.add(imgNodePlay);



    // For each of the ui comp objects create a group and add the crop and bounding box
    for (let i = 0; i < guiNode.uiCompObjects.length; i++) {
      currUICompObject = guiNode.uiCompObjects[i];
      if (currUICompObject.is_CompoundElement) continue;
      comp_bounds = currUICompObject['comp_bounds'];
      comp_label = currUICompObject['comp_label'];
      let a = comp_bounds;
      let factor =
        (1440 / guiNode.image.width) *
        (1 / scaling_factor) *
        (guiNode.image.width / 540) *
        (1 / scalePlayerContainer);
      normalizedA = a.map(function (x) {
        return x / factor;
      });
      let width = normalizedA[2] - normalizedA[0];
      let height = normalizedA[3] - normalizedA[1];
       if (showUICinPreview.value) {
        stroke_color = component_color_mapping[comp_label] || 'black';
        stroke_color = 'blue';
      } else {
        stroke_color = undefined;
      }
      name = `${guiNode.id}_${i}`;
      guiNode.uiCompObjects[i]['id'] = name;

      if (currUICompObject.isGroup) {
              stroke_color = 'black';
            } else if (currUICompObject.isCustom) {
              stroke_color = 'green';
            }
      if (!showUICinPreview.value) {
          stroke_color = undefined;
      }      
            var crop =
              !currUICompObject.isGroup && !guiNode.isBlank
                ? getCroppedComponent(
                    imgNodePlay,
                    guiNode.image,
                    normalizedA[0],
                    normalizedA[1],
                    width,
                    height,
                    normalizedA[0] *
                      (1 / scaling_factor) *
                      (guiNode.image.width / 540) *
                      (1 / scalePlayerContainer),
                    normalizedA[1] *
                      (1 / scaling_factor) *
                      (guiNode.image.width / 540) *
                      (1 / scalePlayerContainer),
                    width *
                      (1 / scaling_factor) *
                      (guiNode.image.width / 540) *
                      (1 / scalePlayerContainer),
                    height *
                      (1 / scaling_factor) *
                      (guiNode.image.width / 540) *
                      (1 / scalePlayerContainer),
                    false
                  )
                : new Konva.Rect({
                    x: normalizedA[0],
                    y: normalizedA[1],
                    width: width,
                    height: height,
                    fill: currUICompObject.bg_color || '#ffffff',
                  });
            crop.setAttr('comp_label', comp_label);
            crop.setAttr('x', 0);
            crop.setAttr('y', 0);
            crop.visible(true);

            var box2Play = new Konva.Rect({
              x: 0, 
              y: 0,
              width: width,
              height: height,
              stroke_ori: stroke_color,
              stroke: stroke_color,
              strokeWidth: 2,
              opacity: 0.3,
              id: name,
              name: name,
            });


            //Use the updated comp positions to change the group position
            updated_comp_bounds = currUICompObject['updated_comp_bounds'];
            let a1 = updated_comp_bounds;
            let factor1 =
              (1440 / guiNode.image.width) *
              (1 / scaling_factor) *
              (guiNode.image.width / 540) *
              (1 / scalePlayerContainer);
            normalizedA1 = a1.map(function (x) {
              return x / factor1;
            });
            let width1 = normalizedA1[2] - normalizedA1[0];
            let height1 = normalizedA1[3] - normalizedA1[1];

            var compGroup = new Konva.Group({
              draggable: true,
              id: name,
              name: name,
              x: normalizedA1[0],
              y: normalizedA1[1],
              width: width1,
              height: height1,
              id: name,
              name: name,
            });
            compGroup.setAttr('editable', true);

            // Create listeners for the custom components
            if (currUICompObject.isCustom) {
               stroke_color = 'black';
               if (currUICompObject.comp_label === 'Text Button') {
                  compGroup.setAttr('isStillCrop', true);
                  compGroup.setAttr('extraInformation', {
                    ...currUICompObject.extraInformation,
                    width,
                    height,
                    idToRemove: currUICompObject['id'],
                  });
                  compGroup.on('dblclick', function () {
                    if (this.getAttr('isStillCrop')) {
                      createCustomButton(
                        this.getChildren()[1],
                        addBoxTransitionEventListener,
                        this.getAttr('extraInformation')
                      );

                      this.destroy();
                      let idToRemove = this.getAttr(
                        'extraInformation'
                      ).idToRemove.split('_');
                      idToRemove = idToRemove[0] + '_' + idToRemove[1];
                      let nodeToDestroy = guiNodes.find((g) => g.id === idToRemove);
                      if (nodeToDestroy) {
                        let compToDestroy = nodeToDestroy.uiCompObjects.find(
                          (c) => c.id === this.getAttr('extraInformation').idToRemove
                        );
                        let indexToDestroy = nodeToDestroy.uiCompObjects.indexOf(
                          compToDestroy
                        );
                        nodeToDestroy.uiCompObjects.splice(indexToDestroy, 1);
                      }

                      layerPlay.batchDraw();

                      return;
              }
            });
            // isComplexComp = true;
          } else if (currUICompObject.comp_label === 'Text') {
            compGroup.setAttr('isStillCrop', true);
            compGroup.setAttr('extraInformation', {
              ...currUICompObject.extraInformation,
              width,
              height,
              idToRemove: currUICompObject['id'],
            });
            compGroup.on('dblclick', function () {
              if (this.getAttr('isStillCrop')) {
                createCustomLabel(
                  this.getChildren()[1],
                  addBoxTransitionEventListener,
                  this.getAttr('extraInformation')
                );

                this.destroy();
                let idToRemove = this.getAttr(
                  'extraInformation'
                ).idToRemove.split('_');
                idToRemove = idToRemove[0] + '_' + idToRemove[1];
                let nodeToDestroy = guiNodes.find((g) => g.id === idToRemove);
                if (nodeToDestroy) {
                  let compToDestroy = nodeToDestroy.uiCompObjects.find(
                    (c) => c.id === this.getAttr('extraInformation').idToRemove
                  );
                  let indexToDestroy = nodeToDestroy.uiCompObjects.indexOf(
                    compToDestroy
                  );
                  nodeToDestroy.uiCompObjects.splice(indexToDestroy, 1);
                }

                layerPlay.batchDraw();

                return;
              }
            });
          } else if (currUICompObject.comp_label === 'Input') {
            compGroup.setAttr('isStillCrop', true);
            compGroup.setAttr('extraInformation', {
              ...currUICompObject.extraInformation,
              width,
              height,
              idToRemove: currUICompObject['id'],
            });
            compGroup.on('dblclick', function () {
              if (this.getAttr('isStillCrop')) {
                createCustomInput(
                  this.getChildren()[1],
                  addBoxTransitionEventListener,
                  this.getAttr('extraInformation')
                );

                this.destroy();
                let idToRemove = this.getAttr(
                  'extraInformation'
                ).idToRemove.split('_');
                idToRemove = idToRemove[0] + '_' + idToRemove[1];
                let nodeToDestroy = guiNodes.find((g) => g.id === idToRemove);
                if (nodeToDestroy) {
                  let compToDestroy = nodeToDestroy.uiCompObjects.find(
                    (c) => c.id === this.getAttr('extraInformation').idToRemove
                  );
                  let indexToDestroy = nodeToDestroy.uiCompObjects.indexOf(
                    compToDestroy
                  );
                  nodeToDestroy.uiCompObjects.splice(indexToDestroy, 1);
                }

                layerPlay.batchDraw();

                return;
              }
            });
          }
            } // if custom end

            compGroup.add(crop);
            compGroup.add(box2Play);
            groupPlay.add(compGroup);


            if (currUICompObject.isGroup) {
            } else {
              compGroup.moveToTop();
            }


    } // End for ui comp objects
    addBackButton(layerPlay, groupPlay, guiNode, scalePlayerContainer);
    layerPlay.add(groupPlay);

  layerPlay.batchDraw();
}

function addBox2PlayClickEventHandlers(box2Play, nodeBackButton) {
    for (let t of transitions) {
        if (t.from == box2Play.getAttr('id')) {
          box2Play.setAttr('fill', 'green');
          box2Play.on('mousedown', function () {
              this.getParent().moveToBottom();
              var nextNode = layerPlay.findOne(`#${t.to}`);
              nextNode.moveToTop();
              guiStack.push(this.getParent().getAttr('id'));
              //userSetStartNodeId['id'] = t.to
              var guiNode = guiNodes.find((n) => n.id == t.to);
              currentShownGUINode.value = guiNode;
              if (guiStack) {
                  var nodeBackButton = layerPlay.findOne(
                    `#${nextNode.getAttr('id')}_back_btn`
                  );
                  nodeBackButton.setAttr('fill', 'green');
                  nodeBackButton.setAttr('stroke', 'white');
                  nodeBackButton.setAttr('strokeWidth', 2);
                  nodeBackButton.setAttr('opacity', 0.2);
                  nodeBackButton.on('mouseover', function () {
                      document.body.style.cursor = 'pointer';
                        });
                  nodeBackButton.on('mouseout', function () {
                      document.body.style.cursor = 'default';
                    });
                  }
              layerPlay.draw();
            });
          box2Play.on('mouseover', function () {
              document.body.style.cursor = 'pointer';
          });
          box2Play.on('mouseout', function () {
              document.body.style.cursor = 'default';
          });
          }
        }
        
}

function addBox2PlayEventHandlers(box2Play) {
        if (isEditModeOn.value){

          box2Play.on('mousedown', function () {
          if (this.getAttr('clicked')) {
            this.setAttr('stroke', this.getAttr('stroke_ori'));
            this.setAttr('fill', undefined);
            this.setAttr('clicked', false);
            currentSelectedComp.value = null;
          } else {
            this.setAttr('stroke', 'green');
            this.setAttr('fill', 'green');
            this.setAttr('clicked', true);
            if (currentSelectedComp.value) {
              if (currentSelectedComp.value.getParent() != this.getParent()) {
                addTransitionArrow(currentSelectedComp.value, this);
                this.setAttr('stroke', this.getAttr('stroke_ori'));
                currentSelectedComp.value.setAttr(
                  'stroke',
                  currentSelectedComp.value.getAttr('stroke_ori')
                );
                currentSelectedComp.value.setAttr('fill', undefined);
                this.setAttr('fill', undefined);
                this.setAttr('clicked', false);
                currentSelectedComp.value = null;
              } else {
              
                if (currentSelectedComp.value != this) {
                  currentSelectedComp.value.setAttr(
                    'stroke',
                    currentSelectedComp.value.getAttr('stroke_ori')
                  );
                  currentSelectedComp.value.setAttr('fill', undefined);
                  currentSelectedComp.value.setAttr('clicked', false);
                }
                currentSelectedComp.value = this;
              }
            } else {
              currentSelectedComp.value = this;
            }
          }
          layerPlay.batchDraw();
        });
        } else {
          for (let t of transitions) {
          if (t.from == box2Play.getAttr('id')) {
            box2Play.setAttr('fill', 'green');
            box2Play.on('mousedown', function () {
              this.getParent().moveToBottom();
              var nextNode = layerPlay.findOne(`#${t.to}`);
              nextNode.moveToTop();
              guiStack.push(this.getParent().getAttr('id'));
              userSetStartNodeId['id'] = t.to
              if (guiStack) {
                var nodeBackButton = layerPlay.findOne(
                  `#${nextNode.getAttr('id')}_back_btn`
                );
                nodeBackButton.setAttr('fill', 'green');
                nodeBackButton.setAttr('stroke', 'white');
                nodeBackButton.setAttr('strokeWidth', 2);
                nodeBackButton.setAttr('opacity', 0.2);
                nodeBackButton.on('mouseover', function () {
                  document.body.style.cursor = 'pointer';
                });
                nodeBackButton.on('mouseout', function () {
                  document.body.style.cursor = 'default';
                });
              }
              layerPlay.draw();
            });
            box2Play.on('mouseover', function () {
              document.body.style.cursor = 'pointer';
            });
            box2Play.on('mouseout', function () {
              document.body.style.cursor = 'default';
            });
          }
        }
        }
}


function addBackButton(
  layerPlay,
  groupPlay,
  guiNode,
  scalingPlayer
) {
  let a = [130, 2395, 520, 2567];
  let factor =
    (1440 / guiNode.image.width) *
    (1 ) *
    (guiNode.image.width / 540) *
    (1 / scalingPlayer);
  normalizedA = a.map(function (x) {
    return x / factor;
  });
  let width = normalizedA[2] - normalizedA[0];
  let height = normalizedA[3] - normalizedA[1];

  if (showUICinPreview.value) {
    stroke_color = 'white';
  } else {
    stroke_color = undefined;
  }
  name = `${guiNode.id}_back_btn`;
  var backButton = new Konva.Rect({
    x: normalizedA[0],
    y: normalizedA[1],
    width: width,
    height: height,
    opacity: 0.05,
    id: name,
    name: name,
  });
  groupPlay.add(backButton);
 
  backButton.on('mousedown', function () {
    var lastGuiID = guiStack.value.pop();
    if (lastGuiID) {
      var lastNode = layerPlay.findOne(`#${lastGuiID}`);
      lastNode.moveToTop();
      currentShownGUINode.value = guiNodes.filter(n => lastGuiID.includes(n.id))[0];
      layerPlay.draw();
    }
  });
}


function getUICompObjects(
  jsonDataCombined,
  jsonDataSemantic,
  jsonDataCombinedExtended
) {
  uiCompObjects = [];
  compLabelParents = JSONPath({
    path: '$..componentLabel^',
    json: jsonDataSemantic,
  });
  if (jsonDataCombinedExtended) {
    compLabelParents = jsonDataCombinedExtended['ui_comps'];
    let uiCompGroups = getUICompGroups(jsonDataCombinedExtended);
    uiCompGroups.forEach((g) => {
      uiCompObjects.push(g);
    });
  }
  for (i = 0; i < compLabelParents.length; i++) {
    currCompLabelParent = compLabelParents[i];
    var hasChildren = Boolean(currCompLabelParent['children']);
    var isBackgroundImage =
      currCompLabelParent['componentLabel'] === 'Background Image';
    var isCompoundElement = hasChildren || isBackgroundImage;
    var extraInformation = {};
    let isCustom = false;
    if (currCompLabelParent['componentLabel'] === 'Text') {
      extraInformation = {
        text: currCompLabelParent.text,
        textColor: currCompLabelParent.text_color,
        fontSize: currCompLabelParent.font_size,
      };
      isCustom = true;
    } else if (currCompLabelParent['componentLabel'] === 'Text Button') {
      extraInformation = {
        text: currCompLabelParent.text,
        textColor: currCompLabelParent.text_color,
        fontSize: currCompLabelParent.font_size,
        buttonColor: currCompLabelParent.bg_color,
      };
      isCustom = true;
    } else if (
      currCompLabelParent['componentLabel'] === 'Input' &&
      currCompLabelParent['class'].includes('Text')
    ) {
      //input
      extraInformation = {
        text: currCompLabelParent.text_updated,
        textColor: currCompLabelParent.text_color,
        fontSize: currCompLabelParent.font_size,
        inputColor: currCompLabelParent.bg_color,
      };
      isCustom = true;
    }
    
    uiCompObjects.push({
      comp_label: currCompLabelParent['componentLabel'],
      comp_bounds: currCompLabelParent['bounds'],
      updated_comp_bounds: currCompLabelParent['bounds'],
      has_children: Boolean(hasChildren),
      is_CompoundElement: isCompoundElement,
      plain_json: currCompLabelParent,
      crop_group: undefined,
      extraInformation,
      isCustom,
    });
  }
  return uiCompObjects;
}


function getUICompGroups(jsonDataCombinedExtended = null) {
  if (!jsonDataCombinedExtended) return null;
  let uiCompGroups = [];
  const groupsJson = jsonDataCombinedExtended['ui_comp_groups'];
  groupsJson.forEach((group, i) => {
    uiCompGroups.push({
      comp_label: group['componentLabel'],
      comp_bounds: group['bounds'],
      updated_comp_bounds: group['bounds'],
      bg_color: group['bg_color'],
      isGroup: true,
      crop_group: undefined,
      has_children: false,
      is_CompoundElement: false,
    });
  });
  return uiCompGroups;
}

function addTransitionToKonva(transition) {
  var transitionSourceNodes = layerPlay.find(`#${transition.from}`);
  var boxSources = transitionSourceNodes.getChildren().filter(node => node.getClassName() === 'Rect');
  var boxSource = boxSources[0];
  boxSource.setAttr('fill', 'green');
  layerPlay.batchDraw();
  var transitionSourceNodes = layerPlay.find(`#${transition.from}`);
  boxSource.on('mousedown', function () {
              //this.getParent().moveToBottom();
              var nextNode = layerPlay.findOne(`#${transition.to}`);
              nextNode.moveToTop();
              currentNode = this;
              while (!currentNode.getAttr('master')) {
                  currentNode = currentNode.getParent();
              }
              guiStack.value.push(currentNode.getAttr('id'));
              //userSetStartNodeId['id'] = t.to
              var guiNode = guiNodes.find((n) => n.id == transition.to);
              currentShownGUINode.value = guiNode;
              if (guiStack.value) {
                  var nodeBackButton = layerPlay.findOne(
                    `#${nextNode.getAttr('id')}_back_btn`
                  );
                  nodeBackButton.setAttr('fill', 'green');
                  nodeBackButton.setAttr('stroke', 'white');
                  nodeBackButton.setAttr('strokeWidth', 2);
                  nodeBackButton.setAttr('opacity', 0.2);
                  nodeBackButton.on('mouseover', function () {
                    document.body.style.cursor = 'pointer';
                  });
                  nodeBackButton.on('mouseout', function () {
                    document.body.style.cursor = 'default';
                  });
                }
              layerPlay.draw();
            });
          boxSource.on('mouseover', function () {
              document.body.style.cursor = 'pointer';
          });
          boxSource.on('mouseout', function () {
              document.body.style.cursor = 'default';
          });
          
        
}



function removeUIComponent(uiComponent, isParent = false) {
  // UIcomponent is the clickable rectangle, we first obtain the group parent

  var uiCompParent = uiComponent.getParent();
  if (isParent) {
    uiCompParent = uiComponent;
  }
  var splitIds = uiCompParent.getAttr('id').split('_');
  var guiNodeId = splitIds[0] + '_' + splitIds[1];
  //Find guiNode and remove the ui component from the data model
  var guiNode = guiNodes.find((n) => n.id == guiNodeId);
  var uiCompObject = guiNode.uiCompObjects.find(
    (n) => n['id'] == uiCompParent.getAttr('id')
  );
  var uiCompObjectIndex = guiNode.uiCompObjects.indexOf(uiCompObject);
  guiNode.uiCompObjects.splice(uiCompObjectIndex, 1);
  // Find all outgoing transitions of the ui component and remove them in konva and in the model
  matches = transitions.filter((t) => t.from == uiCompParent.getAttr('id'));
  var arrowNodes = matches.map((t) => layer.findOne(`#${t.id}`));
  for (i = 0; i < arrowNodes.length; i++) {
    arrowNodes[i].remove();
  }
  matchesIndexes = matches.map((m) => transitions.indexOf(m));
  while (matchesIndexes.length) {
    transitions.splice(matchesIndexes.pop(), 1);
  }
  // Remove from Konva

  uiCompParent.remove();
  currentShape = null;
  currentSelectedComp.value = null;
  layerPlay.batchDraw();
}

function markUIComponent(uiComponent, isParent = false) {
  if(currentSelectedComp.value != uiComponent) {
      if (currentSelectedComp.value) {
        currentSelectedComp.value.setAttr('fill', undefined);
      }
      uiComponent.setAttr('fill', 'green');
      currentSelectedComp.value = uiComponent;
  } else {
      uiComponent.setAttr('fill', undefined);
      currentSelectedComp.value = null;
  }
  layerPlay.batchDraw();
}

function removeAllTransitionsForGUINode(guiNode) {
  mappings = transitions.map((t) => [t.to, t.from]);
  matches = transitions.filter(
    (t) => t.to == guiNode.id || t.from.includes(guiNode.id)
  );
  for(i = 0; i < matches.length; i++) {
    var transitionSourceNodes = layerPlay.find(`#${matches[i].from}`);
    var boxSources = transitionSourceNodes.getChildren().filter(node => node.getClassName() === 'Rect');
    var boxSource = boxSources[0];
    boxSource.setAttr('fill', undefined);
    boxSource.off('mousedown');
    boxSource.off('mouseover');
  }
  matchesIndexes = matches.map((m) => transitions.indexOf(m));
  while (matchesIndexes.length) {
    transitions.splice(matchesIndexes.pop(), 1);
  }
}

function deleteGuiNode(currentShape, isParent = false, guiNodeId = '') {
  let id = isParent ? guiNodeId : currentShape.getParent().getAttr('id');
  guiNode = guiNodes.find((n) => id.includes(n.id));
  guiNodeIndex = guiNodes.indexOf(guiNode);
  guiNodes.splice(guiNodeIndex, 1);
  while (!currentShape.getAttr('master')) {
    currentShape = currentShape.getParent();
  }
  currentShape.remove();
  removeAllTransitionsForGUINode(guiNode);
  currentShape = null;

  currentSelectedComp.value = null;
  if (guiNodes.length <= 1) {
    currentShownGUINode.value = null;
    hideGUISummaryButton();
    hideGUIButtons();
  } else {
    currentShownGUINode.value = guiNodes[0];
  }
}


function addBoxTransitionEventListener(e, box) {
  //Only respond if we click the shape with left click
  if (e.evt.button == 0) {
    if (box.getAttr('clicked')) {
      box.setAttr('stroke', box.getAttr('stroke_ori'));
      box.setAttr('fill', undefined);
      box.setAttr('clicked', false);
      currentSelectedComp.value = null;
    } else {
      box.setAttr('stroke', 'green');
      box.setAttr('fill', 'green');
      box.setAttr('clicked', true);
      if (currentSelectedComp.value) {

        if (
          currentSelectedComp.value.getAttr('id').split('_')[1] !=
          box.getAttr('id').split('_')[1]
        ) {
          addTransitionArrow(currentSelectedComp.value, box);
          box.setAttr('stroke', box.getAttr('stroke_ori'));
          currentSelectedComp.value.setAttr(
            'stroke',
            currentSelectedComp.value.getAttr('stroke_ori')
          );
          currentSelectedComp.value.setAttr('fill', undefined);
          box.setAttr('fill', undefined);
          box.setAttr('clicked', false);
          currentSelectedComp.value = null;
        } else {
          if (currentSelectedComp.value != box) {
            currentSelectedComp.value.setAttr(
              'stroke',
              currentSelectedComp.value.getAttr('stroke_ori')
            );
            currentSelectedComp.value.setAttr('fill', undefined);
            currentSelectedComp.value.setAttr('clicked', false);
          }
          currentSelectedComp.value = box;
        }
      } else {
        currentSelectedComp.value = box;
      }
    }
  }
}


module.exports = {
  getUICompObjects,
  addGUIToKonva,
  addTransitionToKonva,
  removeUIComponent,
  markUIComponent,
  removeAllTransitionsForGUINode,
  deleteGuiNode,
 };