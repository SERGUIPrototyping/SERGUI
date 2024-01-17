const Konva = require('konva');
var isEditModeOn = { value: true };
var showGUIReqSummary = { value: true };
var showUICinPreview = { value: false };
var width = 1870;
var height = 2000;

var currentSelectedComp = { value: null };

var graph = null;
var guiNodes = [];
var transitions = [];

var blockSnapSize = 30;
var shadowOffset = 10;
var tween = null;
var scalePlayer = {value: null};
const baseURL = "http://www.sergui-tool.com/static/resources"

const CHAT_MSG_DELAY_MAX = 6000
const CHAT_MSG_DELAY_MIN = 2000

const MAX_PLAYER_SCALE = 0.92;

var userSetStartNodeId = {};

var currentShownGUINode = {value : null};

component_color_mapping = {
  'Background Image': 'red',
  Image: 'pink',
  Input: 'yellow',
  'Text Button': 'blue',
  Button: 'blue',
  Text: 'green',
};

var stagePlay = new Konva.Stage({
    container: 'container-konva-player',
  });

 var stageAspects = new Konva.Stage({
        container: "aspect-gui-container-rendering",
      });
 var layerAspects = new Konva.Layer();
stageAspects.add(layerAspects);

var layerPlay = new Konva.Layer();

stagePlay.add(layerPlay);

guiStack = {value: []};

currentGUIReqSummary = {value: null};

    var arrowImg = new Image();
    arrowImg.onload = function () {
    }
    arrowImg.src = `http://sergui-tool.com/static/resources/arrow_image/arrow.jpeg`;

importHelper = {
  guisInitialized: [],
  guisLoaded: [],
};

module.exports['vars'] = {
  isEditModeOn,
  showUICinPreview,
  width,
  height,
  currentSelectedComp,
  graph,
  guiNodes,
  transitions,
  blockSnapSize,
  shadowOffset,
  tween,
  userSetStartNodeId,
  component_color_mapping,
  guiStack,
  importHelper,
  currentShownGUINode,
  CHAT_MSG_DELAY_MAX,
  CHAT_MSG_DELAY_MIN,
  stagePlay,
  layerPlay,
  MAX_PLAYER_SCALE,
  scalePlayer,
  currentGUIReqSummary,
  showGUIReqSummary,
  stageAspects,
  layerAspects,
  arrowImg,
  baseURL,
};
