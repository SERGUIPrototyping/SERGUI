const Konva = require('konva');
const { vars } = require('./vars');
const { guiNodes, layerPlay, stagePlay } = vars;
const { getNextId } = require('./helpers');

function createCustomLabel(
  currentShape,
  addBoxTransitionEventListener,
  extraInformation = null
) {
  let labelText = 'Sample Text';
  let fontSize = 12;
  let fontColor = '#000000';

  if (extraInformation) {
    labelText = extraInformation.text;
    fontSize = extraInformation.fontSize;
    fontColor = extraInformation.textColor;
  }

  // Remove guiNode first from the data model
  guiNode = guiNodes.find(
    (n) => n.id == currentShape.getParent().getParent().getAttr('id')
  );
  let currShapeParent = currentShape.getParent();
  var labelGroup = currShapeParent.clone();
  labelGroup.destroyChildren();
  var newId = getNextId(guiNode);
  newId = guiNode['id'] + '_' + newId;
  labelGroup.setAttr('name', newId);
  labelGroup.setAttr('id', newId);
  labelGroup.setAttr('visible', true);

  //create the two children: text and colored box
  let text = new Konva.Text({
    text: labelText,
    id: newId + '_img',
    name: newId + '_img',
    fontSize,
    fill: fontColor,
  });

  //limit the text width
  if (text.width() >= 250) {
    text.width(250);
  }

  if (extraInformation) {
    if (text.width() > extraInformation.width) {
      text.width(extraInformation.width);
    }
  }

  let box = new Konva.Rect({
    x: 0, //normalizedA[0] ,
    y: 0, //normalizedA[1] ,
    width: text.width(),
    height: text.height(),
    stroke_ori: 'gray',
    stroke: 'gray',
    strokeWidth: 2,
    opacity: 0.3,
    id: newId,
    name: newId,
  });

  //set editable on box to true
  box.setAttr('editable', true);


  //add children to group
  labelGroup.add(text);
  labelGroup.add(box);
  var newOffset = extraInformation ? 0 : 20;
  labelGroup.setAttr('x', labelGroup.getAttr('x') + newOffset);
  labelGroup.setAttr('y', labelGroup.getAttr('y') + newOffset);
  labelGroup.width(box.width());
  labelGroup.height(box.height());

  labelGroup.setAttr('isCustom', true);

  //add listener for editing the label
  labelGroup.off('dblclick');
  labelGroup.on('dblclick', function () {
    // at first lets find position of text node relative to the stage:
        var textPosition = this.getAbsolutePosition();

        // then lets find position of stage container on the page:
        var stageBox = stagePlay.container().getBoundingClientRect();

        // so position of textarea will be the sum of positions above:
        var areaPosition = {
          x: stageBox.left + textPosition.x,
          y: stageBox.top + textPosition.y,
        };

        // create textarea and style it
        var textarea = document.createElement('textarea');
        document.body.appendChild(textarea);

        textarea.value = text.getAttr('text');
        textarea.style.position = 'absolute';
        textarea.style.top = areaPosition.y + 'px';
        textarea.style.left = areaPosition.x + 'px';
        textarea.style.width = currShapeParent.width() + 'px';
        textarea.style.height = currShapeParent.height() + 'px';
        textarea.style.backgroundColor = "white";
        textarea.style.resize = "none";
        textarea.style.textAlign = "center";

        textarea.focus();

        textarea.addEventListener('keydown', function (e) {
          // hide on enter
          if (e.keyCode === 13) {
            text.text(textarea.value);
            document.body.removeChild(textarea);
          }
          layerPlay.batchDraw();
        });
  });

  //create and add new uiCompObject to data model
  var uiCompObject1 = guiNode.uiCompObjects.find(
    (n) => n['id'] == currentShape.getAttr('id')
  );
  var newCompObj = Object.assign({}, uiCompObject1);
  newCompObj['id'] = newId;
  newCompObj['comp_label'] = 'CustomLabel';
  newCompObj['plain_json'] = {};
  newCompObj['crop_group'] = labelGroup.clone();
  newCompObj['isBlank'] = false;
  newCompObj['isGroup'] = false;
  //newCompObj['is_CompoundElement'] = false;

  guiNode.uiCompObjects.push(newCompObj);
  var currGroup = currentShape.getParent().getParent();

  currGroup.add(labelGroup);
  // labelGroup.moveToTop();
  //fire these two events in order to display component correctly
  labelGroup.fire('dragstart');
  labelGroup.fire('dragend');
  layerPlay.batchDraw();
  if (extraInformation) {
    labelGroup.fire('dblclick');
  }
}

function getLabelCrop(textParam, fontSize, fontColor, width, height) {
  let text = new Konva.Text({
    text: textParam,
    fontSize: fontSize || 12,
    fill: fontColor || '#000000',
  });

  if (text.getTextWidth() > width) {
    text.width(width);
  }

  if (text.getTextHeight() > height) {
    text.height(height);
  }

  return text;
}

function createCustomButton(
  currentShape,
  addBoxTransitionEventListener,
  extraInformation = null
) {
  let buttonText = 'Sample Text';
  let fontSize = 12;
  let fontColor = '#000000';
  let buttonColor = '#ffffff';

  if (extraInformation) {
    buttonText = extraInformation.text;
    fontSize = extraInformation.fontSize;
    fontColor = extraInformation.textColor;
    buttonColor = extraInformation.buttonColor;
  }

  // Remove guiNode first from the data model
  guiNode = guiNodes.find(
    (n) => n.id == currentShape.getParent().getParent().getAttr('id')
  );
  let currShapeParent = currentShape.getParent();
  var buttonGroup = currShapeParent.clone();
  buttonGroup.destroyChildren();
  var newId = getNextId(guiNode);
  newId = guiNode['id'] + '_' + newId;
  buttonGroup.setAttr('name', newId);
  buttonGroup.setAttr('id', newId);
  buttonGroup.setAttr('visible', true);

  buttonGroup.setAttr('isCustom', true);

  let text = new Konva.Text({
    text: buttonText,
    id: newId + '_img',
    name: newId + '_img',
    fontSize,
    fill: fontColor,
    verticalAlign: 'middle',
    align: 'center',
  });

  let realWidth = text.getTextWidth();
  let realHeight = text.getTextHeight();

  let buttonExtraWidth = realWidth * 2;
  let buttonExtraHeight = realHeight * 3;

  text.width(buttonExtraWidth);
  text.height(buttonExtraHeight);

  //limit the text width
  if (text.width() >= 250) {
    text.width(250);
  }

  if (extraInformation) {
    text.width(extraInformation.width);
    text.height(extraInformation.height);
  }


  let buttonFill = new Konva.Rect({
    width: text.width(),
    height: text.height(),
    fill: buttonColor,
    cornerRadius: text.width() / 15,
    id: newId + '_img',
    name: newId + '_img',
  });

  if (extraInformation) {
    buttonFill.setAttr('fixedWidth', buttonFill.width());
    buttonFill.setAttr('fixedHeight', buttonFill.height());
  }

  let box = new Konva.Rect({
    x: buttonFill.x(), 
    y: buttonFill.y(),
    width: buttonFill.width(),
    height: buttonFill.height(),
    stroke_ori: 'gray',
    stroke: 'gray',
    strokeWidth: 2,
    opacity: 0.3,
    id: newId,
    name: newId,
  });

  //set editable on box to true
  box.setAttr('editable', true);


  //add children to group
  buttonGroup.add(buttonFill);
  buttonGroup.add(text);

  buttonGroup.add(box);
  var newOffset = extraInformation ? 0 : 20;
  buttonGroup.setAttr('x', buttonGroup.getAttr('x') + newOffset);
  buttonGroup.setAttr('y', buttonGroup.getAttr('y') + newOffset);
  buttonGroup.width(box.width());
  buttonGroup.height(box.height());
  text.setAttr('align', 'center');
  text.setAttr('verticalAlign', 'middle');

  //add listener for editing the label
  buttonGroup.off('dblclick');
  buttonGroup.on('dblclick', function () {
        // at first lets find position of text node relative to the stage:
        var textPosition = this.getAbsolutePosition();

        // then lets find position of stage container on the page:
        var stageBox = stagePlay.container().getBoundingClientRect();

        // so position of textarea will be the sum of positions above:
        var areaPosition = {
          x: stageBox.left + textPosition.x,
          y: stageBox.top + textPosition.y,
        };

        // create textarea and style it
        var textarea = document.createElement('textarea');
        document.body.appendChild(textarea);

        textarea.value = text.getAttr('text');
        textarea.style.position = 'absolute';
        textarea.style.top = areaPosition.y + 'px';
        textarea.style.left = areaPosition.x + 'px';
        textarea.style.width = buttonFill.width() + 'px';
        textarea.style.height = buttonFill.height() + 'px';
        textarea.style.backgroundColor = "white";
        textarea.style.resize = "none";
        textarea.style.textAlign = "center";

        textarea.focus();

        textarea.addEventListener('keydown', function (e) {
          // hide on enter
          if (e.keyCode === 13) {
            text.text(textarea.value);
            document.body.removeChild(textarea);
          }
          layerPlay.batchDraw();
        });
  });

  //create and add new uiCompObject to data model
  var uiCompObject1 = guiNode.uiCompObjects.find(
    (n) => n['id'] == currentShape.getAttr('id')
  );
  var newCompObj = Object.assign({}, uiCompObject1);
  newCompObj['id'] = newId;
  newCompObj['comp_label'] = 'CustomButton';
  newCompObj['plain_json'] = {};
  newCompObj['crop_group'] = buttonGroup.clone();
  newCompObj['isBlank'] = false;
  newCompObj['isGroup'] = false;

  guiNode.uiCompObjects.push(newCompObj);
  var currGroup = currentShape.getParent().getParent();

  currGroup.add(buttonGroup);
 
  if (extraInformation) {
    buttonGroup.fire('dblclick');
  }

  layerPlay.batchDraw();

}

function getButtonCrop(
  textParam,
  fontSize,
  fontColor,
  buttonColor,
  width,
  height,
  boxId,
  addBoxTransitionEventListener
) {
  let text = new Konva.Text({
    text: textParam,
    fontSize,
    fill: fontColor,
    verticalAlign: 'middle',
    align: 'center',
    height,
    width,
    id: boxId + '_img',
    name: boxId + '_img',
  });

  let buttonFill = new Konva.Rect({
    width,
    height,
    fill: buttonColor,
    cornerRadius: text.width() / 15,
    id: boxId + '_img',
    name: boxId + '_img',
  });

  buttonFill.setAttr('fixedWidth', width);
  buttonFill.setAttr('fixedHeight', height);

  let box = new Konva.Rect({
    x: buttonFill.x(),
    y: buttonFill.y(),
    width: buttonFill.width(),
    height: buttonFill.height(),
    stroke_ori: 'green',
    stroke: 'green',
    strokeWidth: 2,
    opacity: 0.3,
    id: boxId,
    name: boxId,
  });

  //set editable on box to true
  box.setAttr('editable', true);

  box.on('mousedown', (e) => addBoxTransitionEventListener(e, box));

  return [buttonFill, text, box];
}

function createCustomInput(
  currentShape,
  addBoxTransitionEventListener,
  extraInformation = null
) {
  let inputText = 'Sample Text';
  let fontSize = 12;
  let fontColor = '#ffffff';
  let inputColor = '#cccccc';
  let inputSize = 'full';

  if (extraInformation) {
    inputText = extraInformation.text;
    fontSize = extraInformation.fontSize;
    fontColor = extraInformation.textColor;
    inputColor = extraInformation.inputColor;
  }

  // Remove guiNode first from the data model
  guiNode = guiNodes.find(
    (n) => n.id == currentShape.getParent().getParent().getAttr('id')
  );
  let currShapeParent = currentShape.getParent();
  var inputGroup = currShapeParent.clone();
  inputGroup.destroyChildren();
  var newId = getNextId(guiNode);
  newId = guiNode['id'] + '_' + newId;
  inputGroup.setAttr('name', newId);
  inputGroup.setAttr('id', newId);
  inputGroup.setAttr('visible', true);

  inputGroup.setAttr('isCustom', true);

  let inputExtraHeight = fontSize * 1.5;

  //map width
  let inputWidthMap = {
    full: 250,
    twoThirds: 167,
    half: 125,
    oneThird: 83,
    fourth: 62,
  };

  let inputWidth = inputWidthMap[inputSize] || 250;

  //create the children: text, colored box, button background
  let text = new Konva.Text({
    text: inputText,
    id: newId + '_img',
    name: newId + '_img',
    fontSize,
    fill: fontColor,
    x: 5,
    verticalAlign: 'middle',
  });

  //limit the text width

  text.width(inputWidth - 10);

  text.height(text.getTextHeight() + inputExtraHeight);

  if (extraInformation) {
    text.width(extraInformation.width);
    text.height(extraInformation.height);
  }

  let inputFill = new Konva.Rect({
    x: 0, 
    y: 0,
    width: inputWidth,
    height: text.height(),
    fill: inputColor,
    opacity: 0.3,
    id: newId + '_img',
    name: newId + '_img',
  });

  inputFill.setAttr('inputSize', inputSize);

  let box = new Konva.Rect({
    x: inputFill.x(), 
    y: inputFill.y(), 
    width: inputFill.width(),
    height: inputFill.height(),
    stroke_ori: 'gray',
    stroke: 'gray',
    strokeWidth: 2,
    opacity: 0.3,
    id: newId,
    name: newId,
  });

  //set editable on box to true
  box.setAttr('editable', true);

  box.on('mousedown', (e) => addBoxTransitionEventListener(e, box));

  //add children to group
  inputGroup.add(inputFill);
  inputGroup.add(text);

  inputGroup.add(box);
  var newOffset = extraInformation ? 0 : 20;
  inputGroup.setAttr('x', inputGroup.getAttr('x') + newOffset);
  inputGroup.setAttr('y', inputGroup.getAttr('y') + newOffset);
  inputGroup.width(box.width());
  inputGroup.height(box.height());

  //add listener for editing the label
  inputGroup.off('dblclick');
  inputGroup.on('dblclick', function () {
        // at first lets find position of text node relative to the stage:
        var textPosition = this.getAbsolutePosition();

        // then lets find position of stage container on the page:
        var stageBox = stagePlay.container().getBoundingClientRect();

        // so position of textarea will be the sum of positions above:
        var areaPosition = {
          x: stageBox.left + textPosition.x,
          y: stageBox.top + textPosition.y,
        };

        // create textarea and style it
        var textarea = document.createElement('textarea');
        document.body.appendChild(textarea);

        textarea.value = text.getAttr('text');
        textarea.style.position = 'absolute';
        textarea.style.top = areaPosition.y + 'px';
        textarea.style.left = areaPosition.x + 'px';
        textarea.style.width = inputFill.width() + 'px';
        textarea.style.height = inputFill.height() + 'px';
        textarea.style.backgroundColor = "white";
        textarea.style.resize = "none";
        textarea.style.textAlign = "center";

        textarea.focus();

        textarea.addEventListener('keydown', function (e) {
          // hide on enter
          if (e.keyCode === 13) {
            text.text(textarea.value);
            document.body.removeChild(textarea);
          }
          layerPlay.batchDraw();
        });


  });

  //create and add new uiCompObject to data model
  var uiCompObject1 = guiNode.uiCompObjects.find(
    (n) => n['id'] == currentShape.getAttr('id')
  );
  var newCompObj = Object.assign({}, uiCompObject1);
  newCompObj['id'] = newId;
  newCompObj['comp_label'] = 'CustomInput';
  newCompObj['plain_json'] = {};
  newCompObj['crop_group'] = inputGroup.clone();
  newCompObj['isBlank'] = false;
  newCompObj['isGroup'] = false;

  guiNode.uiCompObjects.push(newCompObj);
  var currGroup = currentShape.getParent().getParent();

  currGroup.add(inputGroup);
  //fire these two events in order to display component correctly
  inputGroup.fire('dragstart');
  inputGroup.fire('dragend');
  if (extraInformation) {
    inputGroup.fire('dblclick');
  }
  layerPlay.batchDraw();

}

function getInputCrop(
  textParam,
  fontSize,
  fontColor,
  inputColor,
  width,
  height
) {
  let text = new Konva.Text({
    text: textParam,
    width,
    height,
    fontSize,
    fill: fontColor,
    x: 5,
    verticalAlign: 'middle',
  });

  let inputFill = new Konva.Rect({
    x: 0, 
    y: 0, 
    width,
    height: text.height(),
    fill: inputColor,
    opacity: 0.3,
  });

  return [inputFill, text];
}

module.exports = {
  createCustomLabel,
  getLabelCrop,
  createCustomButton,
  getButtonCrop,
  createCustomInput,
  getInputCrop,
};
