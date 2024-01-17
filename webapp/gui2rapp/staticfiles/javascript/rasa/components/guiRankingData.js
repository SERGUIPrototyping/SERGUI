const { vars } = require('../../sergui/vars');

var {
    currentGUIReqSummary,
    showGUIReqSummary,
    guiNodes,
    layerPlay,
    stageAspects,
    layerAspects,
    gfb_top_k_gui_indexes,
    top_k_annotation_gui_indexes,
    top_k_annotation_feature_indexes,
    baseURL,
} = vars;

/**
 *  Renders the GUI ranking data to the workbench container
 */
function renderGUIRankingData(guiRankingData) {
    setTimeout(() => {
        $('#workbench-wrapper').children().remove();
        searchResultCards = guiRankingData.map((doc) =>
                        searchResultCard(doc['index'], doc['rank'], doc['score']));
        $('#workbench-wrapper').append(`
        <div id="container-workbench" class="row text-center text-lg-left" style="margin-top:2px; height:100%;overflow-y:scroll">        
      </div>`)
        $('#container-workbench').append(searchResultCards).hide().fadeIn(1300);
        scrollToTopOfRankingResults();
        $('#container-workbench').css("background-color", '#e6fff2');
    }, 1000);
}

function scrollToTopOfRankingResults() {
    const rankingResultsDiv = document.getElementById("container-workbench-wrapper");
   $("#container-workbench-wrapper").animate({ scrollTop: 0 }, "slow");
}

function searchResultCard(index, rank, conf) {
  return `<div class="col-lg-4 col-md-6 col-12 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}.</p>
      <img class="card-img-top myImages" id="myImg-${index}" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">
            <button id="btn-gui-add-${index}" data-val="${index}" class="btn btn-success p-0" style="width:100%;text-transform: none;" type="submit">Select</button>

          </div>`;
}


function renderGUIRankingDataReselect(guiRankingData) {
    setTimeout(() => {
        $('#workbench-wrapper').children().remove();
        searchResultCards = guiRankingData.map((doc) =>
                        searchResultCardReselect(doc['index'], doc['rank'], doc['score']));
        $('#workbench-wrapper').append(`
        <div id="container-workbench" class="row text-center text-lg-left" style="margin-top:2px; height:100%;overflow-y:scroll">        
      </div>`)
        $('#container-workbench').append(searchResultCards).hide().fadeIn(1300);
        scrollToTopOfRankingResults();
        $('#container-workbench').css("background-color", '#e6fff2');
    }, 1000);
}

function searchResultCardReselect(index, rank, conf) {
  return `<div class="col-lg-4 col-md-6 col-12 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}.</p>
      <img class="card-img-top myImages" id="myImg-${index}" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">
            <button id="btn-gui-reselect-${index}" data-val="${index}" class="btn btn-success p-0" style="width:100%;text-transform: none;" type="submit">Select</button>

          </div>`;
}


function gfbAnnotationCard(index, rank, conf) {
  return `<div class="col-lg-4 col-md-6 col-12 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}.</p>
      <img class="card-img-top myImages" id="myImg-${index}" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">
                     <div>
          <input type="radio" class="custom-btn-1" value="R" name="options-outlined-${rank}" id="success-outlined-${rank}" autocomplete="off">
<label style="width:49%" class="btn btn-outline-success" for="success-outlined-${rank}">+</label>

          <input type="radio" class="custom-btn-2" value="NR" name="options-outlined-${rank}" id="danger-outlined-${rank}" autocomplete="off">
<label style="width:49%" class="btn btn-outline-danger" for="danger-outlined-${rank}">-</label>
</div>


          </div>


        </div>`;
}

function topKFinalAnnotationCard(index, rank, conf) {
  return `<div class="col-lg-4 col-md-6 col-12 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}.</p>
      <img style='margin-bottom:5px' class="card-img-top myImages" id="myImg-${index}" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">
                     <div style="text-align:center">
          <input type="radio" class="custom-btn-1" value="0" name="options-outlined-${rank}" id="button-0-${rank}" autocomplete="off">
<label style="width:30%" class="btn" for="button-0-${rank}">0</label>

          <input type="radio" class="custom-btn-1" value="1" name="options-outlined-${rank}" id="button-1-${rank}" autocomplete="off">
<label style="width:30%" class="btn" for="button-1-${rank}">1</label>
                    <input type="radio" class="custom-btn-1" value="2" name="options-outlined-${rank}" id="button-2-${rank}" autocomplete="off">
<label style="width:30%" class="btn" for="button-2-${rank}">2</label>
</div>


          </div>


        </div>`
}

function renderGUIRankingDataForAnnotation(guiRankingData) {
    setTimeout(() => {
        $('#workbench-wrapper').children().remove();
        gfbAnnotationCards = guiRankingData.map((doc) =>
                        gfbAnnotationCard(doc['index'], doc['rank'], doc['score']));
        $('#workbench-wrapper').append(`
        <div id="container-workbench" class="row text-center text-lg-left" style="margin-top:2px; height:100%;overflow-y:scroll">        
      </div>`)
        $('#container-workbench').append(gfbAnnotationCards).hide().fadeIn(1300);
        gfb_top_k_gui_indexes.value = guiRankingData.map((doc) => doc['index']);
        scrollToTopOfRankingResults();
        $('#container-workbench').css("background-color", '#e6f2ff');
    }, 1000);
}

function renderGUIRankingDataForTopKFinalAnnotation(guiRankingData) {
    setTimeout(() => {
        $('#workbench-wrapper').children().remove();
        topkfinalAnnotationCards = guiRankingData.map((doc) =>
                        topKFinalAnnotationCard(doc['index'], doc['rank'], doc['score']));
        $('#workbench-wrapper').append(`
        <div id="container-workbench" class="row text-center text-lg-left" style="margin-top:2px; height:100%;overflow-y:scroll">        
      </div>`)
        $('#container-workbench').append(topkfinalAnnotationCards).hide().fadeIn(1300);
        top_k_annotation_gui_indexes.value = guiRankingData.map((doc) => doc['index']);
        scrollToTopOfRankingResults();
        $('#container-workbench').css("background-color", '#e6f2ff');
    }, 1000);
}

function addKonvaImage(guiIndex) {
    var stagePlay = new Konva.Stage({
        container: 'konva-workbench',
      });
    var layerPlay = new Konva.Layer();

    stagePlay.add(layerPlay);

    var newImg = new Image();
    newImg.onload = function () {
        drawGUI(this);
    }
    newImg.src = `${baseURL}/combined/${guiIndex}.jpg`;

    function drawGUI(newImg) {
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: newImg,
          width: newImg.width * (540 / newImg.width),
          height: newImg.height * (540 / newImg.width),
        });

        var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
        var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');
        var scalePlayerContainer = 0.60;
        var scaling_factor = 1.0;
        var updatedWidth = realWidth * scalePlayerContainer;
        var updatedHeight = realHeight * scalePlayerContainer;

        imgNodePlay.width(updatedWidth);
        imgNodePlay.height(updatedHeight);
        stagePlay.width(updatedWidth);
        stagePlay.height(updatedHeight);

        $('#konva-workbench').width(updatedWidth).height(updatedHeight);
        layerPlay.add(imgNodePlay);
        layerPlay.batchDraw();
    }
}

function renderExampleGUI(guiIndex) {
    setTimeout(() => {
        $('#workbench-wrapper').children().remove();
  $('#workbench-wrapper').append(`
     <div id="konva-workbench-wrapper" style="overflow-y:scroll;scrollbar-width:none;width:100%;height:80%;display:flex;justify-content:center;align-items:center;">
        <div id="konva-workbench" style='width:0px;height:0px;'></div>
    </div>`)
        addKonvaImage(guiIndex);
    }, 200);
}

function renderFeatureRanking(data) {
        setTimeout(() => {
        $('#workbench-wrapper').children().remove();
        $('#workbench-wrapper').append(`
        <div id="container-workbench" class="row text-center text-lg-left" style="margin-top:2px; height:100%;overflow-y:scroll">        
      </div>`).hide().fadeIn(1300);
         for (var i = 0; i < data.length; i++) {
             $("#container-workbench").append(featureCard(data[i]['rank'], data[i]['gui_id']));
             addKonvaImageAndFeatureWithContainerRanking(data[i]['gui_id'], data[i]['bounds'], 'feature-'+data[i]['rank']);
    }
        scrollToTopOfRankingResults();
        $('#container-workbench').css("background-color", '#e6f2ff');
    }, 1000);
}

function renderTopKFeatureRanking(data) {
        setTimeout(() => {
        $('#workbench-wrapper').children().remove();
        $('#workbench-wrapper').append(`
        <div id="container-workbench" class="row text-center text-lg-left" style="margin-top:2px; height:100%;overflow-y:scroll">        
      </div>`).hide().fadeIn(1300);
         for (var i = 0; i < data.length; i++) {
             $("#container-workbench").append(featureCardTopK(data[i]['rank'], data[i]['gui_id'], data[i]['text'], data[i]['score']));
             addKonvaImageAndFeatureWithContainerRanking(data[i]['gui_id'], data[i]['bounds'], 'feature-'+data[i]['rank']);
    }
        top_k_annotation_feature_indexes.value = data.map((doc) => doc['feature_id']);
        scrollToTopOfRankingResults();
        $('#container-workbench').css("background-color", '#e6f2ff');
    }, 1000);
}

function featureCard(rank, index) {
  return `<div id="feature-card" class="col-lg-4 col-md-6 col-6 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED; width:100%;text-align: center;vertical-align: middle;align-items: center;" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}.</p>
      <div class="card-img-top myImages" id="feature-${rank}"></div>
        <button id="btn-select-feature-${index}" data-val="${index}" class="btn btn-primary p-0" style="width:100%;text-transform: none;" type="submit">Select</button>

          </div> </div>`;
}

function featureCardTopK(rank, index, text, score) {
    return `<div id="feature-card" class="col-lg-4 col-md-6 col-6 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED; width:100%;text-align: center;vertical-align: middle;align-items: center;" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${rank}. (${score})</p>
      <div style="margin-bottom:5px" class="card-img-top myImages" id="feature-${rank}"></div>
                <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:5px">"${text}"</p>
        <div style="text-align:center;width:100%">
          <input type="radio" class="custom-btn-1-1" value="R" name="options-outlined-${rank}" id="success-outlined-${rank}" autocomplete="off">
<label style="width:45%" class="btn btn-outline-success" for="success-outlined-${rank}">+</label>

          <input type="radio" class="custom-btn-2-2" value="NR" name="options-outlined-${rank}" id="danger-outlined-${rank}" autocomplete="off">
<label style="width:45%" class="btn btn-outline-danger" for="danger-outlined-${rank}">-</label>
</div>

          </div> </div>`
}


function addKonvaImageAndFeature(data) {
  var guiIndex = data['gui_id']
  var bounds = data['bounds']
    var stagePlay = new Konva.Stage({
        container: 'konva-workbench',
      });
    var layerPlay = new Konva.Layer();

    stagePlay.add(layerPlay);

    var newImg = new Image();
    newImg.onload = function () {
        drawGUI(this, bounds);
    }
    newImg.src = `${baseURL}/combined/${guiIndex}.jpg`;

    function drawGUI(newImg, bounds) {
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: newImg,
          width: newImg.width * (540 / newImg.width),
          height: newImg.height * (540 / newImg.width),
        });

        var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
        var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');
        var scalePlayerContainer = 0.60;
        var scaling_factor = 1.0;
        var updatedWidth = realWidth * scalePlayerContainer;
        var updatedHeight = realHeight * scalePlayerContainer;

        imgNodePlay.width(updatedWidth);
        imgNodePlay.height(updatedHeight);
        stagePlay.width(updatedWidth);
        stagePlay.height(updatedHeight);

        $('#konva-workbench').width(updatedWidth).height(updatedHeight);
        layerPlay.add(imgNodePlay);


    let factor =
            (1440 / newImg.width) *
            (1 / scaling_factor) *
            (newImg.width / 540) *
            (1 / scalePlayerContainer);
          let a = bounds;
    normalizedA = a.map(function (x) {
            return x / factor;
          });
          let width = normalizedA[2] - normalizedA[0];
          let height = normalizedA[3] - normalizedA[1];
          color = 'red'//'#32CD32';
          padding = 2
           var box2Play = new Konva.Rect({
                  x: normalizedA[0] - padding,
                  y: normalizedA[1] - padding,
                  width: width + padding*2,
                  height: height + padding*2,
                  stroke_ori: color,
                  stroke: color,
                  strokeWidth: 3,
            });
            layerPlay.add(box2Play);

            arrow_x = box2Play.getAttr('x') + box2Play.getAttr('width')/2;

            rect_y_top = box2Play.getAttr('y');
            offset_top = 100;
            offset_arrow_end = 10;
            offset_arrow_start = 40;
            if((rect_y_top-offset_top) <= 0) {
                points = [arrow_x, rect_y_top+box2Play.getAttr('height')+offset_arrow_start, arrow_x,
                            rect_y_top+box2Play.getAttr('height')+offset_arrow_end]
            } else {
                points = [arrow_x, rect_y_top-offset_arrow_start, arrow_x, rect_y_top-offset_arrow_end]
            }
            y_end = box2Play.getAttr('y');
              var arrow = new Konva.Arrow({
            points: points,
            pointerLength: 5,
            pointerWidth: 6,
            fill: color,
            stroke: color,
            strokeWidth: 10,
          });

          layerPlay.add(arrow);
          layerPlay.batchDraw();
    }
}

function renderExampleGUIWithFeature(data) {
    setTimeout(() => {
        $('#workbench-wrapper').children().remove();
  $('#workbench-wrapper').append(`
     <div id="konva-workbench-wrapper" style="overflow-y:scroll;scrollbar-width:none;width:100%;height:80%;display:flex;justify-content:center;align-items:center;">
        <div id="konva-workbench" style='width:0px;height:0px;'></div>
    </div>`)
        addKonvaImageAndFeature(data);
        $('#container-workbench').css("background-color", '#e6f2ff');
    }, 200);
}




function addKonvaImageAndFeatureWithContainerRanking(gui_id, bounds, container_id) {
  var guiIndex = gui_id;
  var bounds = bounds;
    var stage = new Konva.Stage({
        container: container_id,
      });
    var layerPlay = new Konva.Layer();

    stage.add(layerPlay);

    var newImg = new Image();
    newImg.onload = function () {
        drawGUI(this, bounds);
    }
    newImg.src = `${baseURL}/combined/${guiIndex}.jpg`;

    function drawGUI(newImg, bounds) {
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: newImg,
          width: newImg.width * (540 / newImg.width),
          height: newImg.height * (540 / newImg.width),
        });
        var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
        var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');
        var scalePlayerContainer = computeScaling3(realWidth);
        var scaling_factor = 1.0;
        var updatedWidth = realWidth * scalePlayerContainer;
        var updatedHeight = realHeight * scalePlayerContainer;

        imgNodePlay.width(updatedWidth);
        imgNodePlay.height(updatedHeight);
        stage.width(updatedWidth);
        stage.height(updatedHeight);

        $('#'+container_id).width(updatedWidth).height(updatedHeight);
        layerPlay.add(imgNodePlay);


    let factor =
            (1440 / newImg.width) *
            (1 / scaling_factor) *
            (newImg.width / 540) *
            (1 / scalePlayerContainer);
          let a = bounds;
    normalizedA = a.map(function (x) {
            return x / factor;
          });
          let width = normalizedA[2] - normalizedA[0];
          let height = normalizedA[3] - normalizedA[1];
          color = 'red'//'#32CD32';
          padding = 2
           var box2Play = new Konva.Rect({
                  x: normalizedA[0] - padding,
                  y: normalizedA[1] - padding,
                  width: width + padding*2,
                  height: height + padding*2,
                  stroke_ori: color,
                  stroke: color,
                  strokeWidth: 3,
            });
            layerPlay.add(box2Play);

            arrow_x = box2Play.getAttr('x') + box2Play.getAttr('width')/2;

            rect_y_top = box2Play.getAttr('y');
            offset_top = 100;
            offset_arrow_end = 10;
            offset_arrow_start = 40;
            if((rect_y_top-offset_top) <= 0) {
                points = [arrow_x, rect_y_top+box2Play.getAttr('height')+offset_arrow_start, arrow_x,
                            rect_y_top+box2Play.getAttr('height')+offset_arrow_end]
            } else {
                points = [arrow_x, rect_y_top-offset_arrow_start, arrow_x, rect_y_top-offset_arrow_end]
            }
            y_end = box2Play.getAttr('y');
              var arrow = new Konva.Arrow({
            points: points,
            pointerLength: 5,
            pointerWidth: 6,
            fill: color,
            stroke: color,
            strokeWidth: 10,
          });

          layerPlay.add(arrow);
          layerPlay.batchDraw();
    }
}


function addKonvaImageAndFeatureWithContainer(gui_id, bounds, container_id) {
  var guiIndex = gui_id;
  var bounds = bounds;
    var stage = new Konva.Stage({
        container: container_id,
      });
    var layerPlay = new Konva.Layer();

    stage.add(layerPlay);

    var newImg = new Image();
    newImg.onload = function () {
        drawGUI(this, bounds);
    }
    newImg.src = `${baseURL}/combined/${guiIndex}.jpg`;

    function drawGUI(newImg, bounds) {
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: newImg,
          width: newImg.width * (540 / newImg.width),
          height: newImg.height * (540 / newImg.width),
        });
        var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
        var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');
        var scalePlayerContainer = computeScaling1(realWidth);
        var scaling_factor = 1.0;
        var updatedWidth = realWidth * scalePlayerContainer;
        var updatedHeight = realHeight * scalePlayerContainer;

        imgNodePlay.width(updatedWidth);
        imgNodePlay.height(updatedHeight);
        stage.width(updatedWidth);
        stage.height(updatedHeight);

        $('#'+container_id).width(updatedWidth).height(updatedHeight);
        layerPlay.add(imgNodePlay);


    let factor =
            (1440 / newImg.width) *
            (1 / scaling_factor) *
            (newImg.width / 540) *
            (1 / scalePlayerContainer);
          let a = bounds;
    normalizedA = a.map(function (x) {
            return x / factor;
          });
          let width = normalizedA[2] - normalizedA[0];
          let height = normalizedA[3] - normalizedA[1];
          color = 'red'//'#32CD32';
          padding = 2
           var box2Play = new Konva.Rect({
                  x: normalizedA[0] - padding,
                  y: normalizedA[1] - padding,
                  width: width + padding*2,
                  height: height + padding*2,
                  stroke_ori: color,
                  stroke: color,
                  strokeWidth: 3,
            });
            layerPlay.add(box2Play);

            arrow_x = box2Play.getAttr('x') + box2Play.getAttr('width')/2;

            rect_y_top = box2Play.getAttr('y');
            offset_top = 100;
            offset_arrow_end = 10;
            offset_arrow_start = 40;
            if((rect_y_top-offset_top) <= 0) {
                points = [arrow_x, rect_y_top+box2Play.getAttr('height')+offset_arrow_start, arrow_x,
                            rect_y_top+box2Play.getAttr('height')+offset_arrow_end]
            } else {
                points = [arrow_x, rect_y_top-offset_arrow_start, arrow_x, rect_y_top-offset_arrow_end]
            }
            y_end = box2Play.getAttr('y');
              var arrow = new Konva.Arrow({
            points: points,
            pointerLength: 5,
            pointerWidth: 6,
            fill: color,
            stroke: color,
            strokeWidth: 10,
          });

          layerPlay.add(arrow);
          layerPlay.batchDraw();
    }
}

function computeScaling(width) {
    const WIDTH_CORRECTION = 230;
    aspectCardWidth = $('#aspect-card-2').width();
    return (aspectCardWidth) / (width + WIDTH_CORRECTION);
}

function computeScaling1(width) {
    const WIDTH_CORRECTION = 230;
    aspectCardWidth = $('#aspect-card-1').width();
    return (aspectCardWidth) / (width + WIDTH_CORRECTION);
}

function computeScaling3(width) {
    const WIDTH_CORRECTION = 40;
    aspectCardWidth = $('#feature-card').width();
    return (aspectCardWidth) / (width + WIDTH_CORRECTION);
}


function addKonvaImageAndFeatureWithContainer2(gui_id, bounds, container_id) {
  var guiIndex = gui_id;
  var bounds = bounds;
    var stage = new Konva.Stage({
        container: container_id,
      });
    var layerPlay = new Konva.Layer();

    stage.add(layerPlay);

    var newImg = new Image();
    newImg.onload = function () {
        drawGUI(this, bounds);
    }
    newImg.src = `${baseURL}/combined/${guiIndex}.jpg`;

    function drawGUI(newImg, bounds) {
    var imgNodePlay = new Konva.Image({x: 0,y: 0, image: newImg,
          width: newImg.width * (540 / newImg.width),
          height: newImg.height * (540 / newImg.width),
        });
        var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
        var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');


        computedScaling = computeScaling(realWidth);

        var scalePlayerContainer = computeScaling(realWidth);
        var scaling_factor = 1.0;
        var updatedWidth = realWidth * scalePlayerContainer;
        var updatedHeight = realHeight * scalePlayerContainer;

        imgNodePlay.width(updatedWidth);
        imgNodePlay.height(updatedHeight);
        stage.width(updatedWidth);
        stage.height(updatedHeight);

        $('#'+container_id).width(updatedWidth).height(updatedHeight);
        layerPlay.add(imgNodePlay);


    let factor =
            (1440 / newImg.width) *
            (1 / scaling_factor) *
            (newImg.width / 540) *
            (1 / scalePlayerContainer);
          let a = bounds;
    normalizedA = a.map(function (x) {
            return x / factor;
          });
          let width = normalizedA[2] - normalizedA[0];
          let height = normalizedA[3] - normalizedA[1];
          color = 'red'//'#32CD32';
          padding = 2
           var box2Play = new Konva.Rect({
                  x: normalizedA[0] - padding,
                  y: normalizedA[1] - padding,
                  width: width + padding*2,
                  height: height + padding*2,
                  stroke_ori: color,
                  stroke: color,
                  strokeWidth: 3,
            });
            layerPlay.add(box2Play);

            arrow_x = box2Play.getAttr('x') + box2Play.getAttr('width')/2;

            rect_y_top = box2Play.getAttr('y');
            offset_top = 100;
            offset_arrow_end = 10;
            offset_arrow_start = 40;
            if((rect_y_top-offset_top) <= 0) {
                points = [arrow_x, rect_y_top+box2Play.getAttr('height')+offset_arrow_start, arrow_x,
                            rect_y_top+box2Play.getAttr('height')+offset_arrow_end]
            } else {
                points = [arrow_x, rect_y_top-offset_arrow_start, arrow_x, rect_y_top-offset_arrow_end]
            }
            y_end = box2Play.getAttr('y');

              var arrow = new Konva.Arrow({
            points: points,
            pointerLength: 5,
            pointerWidth: 6,
            fill: color,
            stroke: color,
            strokeWidth: 10,
          });

          layerPlay.add(arrow);
          layerPlay.batchDraw();
    }
}

function addAspectGUIsForPDFSummary(aspect_guis) {
    for (var i = 0; i < aspect_guis.length; i++) {
        curr_ag = aspect_guis[i];
        addKonvaImageAndFeatureForSummaryRendering(curr_ag['gui_id'], curr_ag['bounds'], curr_ag['feature_id']);
    }
}



function addKonvaImageAndFeatureForSummaryRendering(gui_id, bounds, feature_id) {
  var guiIndex = gui_id;
  var bounds = bounds;
   
    var newImg = new Image();
    newImg.onload = function () {
        drawGUI(this, bounds, feature_id);
    }
    newImg.src = `${baseURL}/combined/${guiIndex}.jpg`;

    function drawGUI(newImg, bounds, feature_id) {
        var groupPlay = new Konva.Group({name: feature_id, id:feature_id,});
        var imgNodePlay = new Konva.Image({x: 0,y: 0, image: newImg,
              width: newImg.width * (540 / newImg.width),
              height: newImg.height * (540 / newImg.width),
            });
            var realWidth = imgNodePlay.getAttr('width') * imgNodePlay.getAttr('scaleX');
            var realHeight = imgNodePlay.getAttr('height') * imgNodePlay.getAttr('scaleY');


            var scalePlayerContainer = 0.5;
            var scaling_factor = 1.0;
            var updatedWidth = realWidth * scalePlayerContainer;
            var updatedHeight = realHeight * scalePlayerContainer;

            imgNodePlay.width(updatedWidth);
            imgNodePlay.height(updatedHeight);
            stageAspects.width(updatedWidth);
            stageAspects.height(updatedHeight);

            $('#aspect-gui-container-rendering').width(updatedWidth).height(updatedHeight);
            groupPlay.add(imgNodePlay);


    let factor =
            (1440 / newImg.width) *
            (1 / scaling_factor) *
            (newImg.width / 540) *
            (1 / scalePlayerContainer);
          let a = bounds;
    normalizedA = a.map(function (x) {
            return x / factor;
          });
          let width = normalizedA[2] - normalizedA[0];
          let height = normalizedA[3] - normalizedA[1];
          color = 'red'//'#32CD32';
          padding = 2
           var box2Play = new Konva.Rect({
                  x: normalizedA[0] - padding,
                  y: normalizedA[1] - padding,
                  width: width + padding*2,
                  height: height + padding*2,
                  stroke_ori: color,
                  stroke: color,
                  strokeWidth: 3,
            });
            groupPlay.add(box2Play);

            arrow_x = box2Play.getAttr('x') + box2Play.getAttr('width')/2;

            rect_y_top = box2Play.getAttr('y');
            offset_top = 100;
            offset_arrow_end = 10;
            offset_arrow_start = 40;
            if((rect_y_top-offset_top) <= 0) {
                points = [arrow_x, rect_y_top+box2Play.getAttr('height')+offset_arrow_start, arrow_x,
                            rect_y_top+box2Play.getAttr('height')+offset_arrow_end]
            } else {
                points = [arrow_x, rect_y_top-offset_arrow_start, arrow_x, rect_y_top-offset_arrow_end]
            }
            y_end = box2Play.getAttr('y');

              var arrow = new Konva.Arrow({
            points: points,
            pointerLength: 5,
            pointerWidth: 6,
            fill: color,
            stroke: color,
            strokeWidth: 10,
          });

          groupPlay.add(arrow);
          layerAspects.add(groupPlay);
          layerAspects.batchDraw();
    }
}


function aspectGUICard(index, feature_text) {
  return `<div id="aspect-card-1" class="col-lg-4 col-md-6 col-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED; width:75%;text-align: center;vertical-align: middle;align-items: center;" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${index}.</p>
      <div class="card-img-top myImages" id="konva-container-req-${index}"></div>
            <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">"${feature_text}"</p>

          </div> </div>`;
}

function aspectGUICardSummary(index, feature_text) {
  return `<div class="col-lg-4 col-md-6 col-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED; width:75%;text-align: center;vertical-align: middle;align-items: center;" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${index}.</p>
      <div class="card-img-top myImages" id="konva-container-req-summary${index}"></div>
            <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">"${feature_text}"</p>

          </div> </div>`;
}

function selectedGUICard(index, query) {
    return `<div class="col-lg-4 col-md-6 col-6" style="margin-bottom:20px;">
      <div style="padding:8px;background-color:#E3E5ED; width:75%" class="card mb-3 box-shadow">
      <img class="card-img-top myImages" id="myImg-1" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">

          </div> </div>
            <div class="col-lg-8 col-md-8 col-8" style="margin-bottom:20px;text-align: center;vertical-align: middle;align-items: center;justify-content: center; display: flex;" >
                <p style="font-size:30px"><b>Requirements:</b> <i>"${query}"</i></p>
                </div>`
}


function selectedGUICardKonva(index, query) {
    return `<div class="col-lg-4 col-md-6 col-6" style="margin-bottom:20px;">
      <div style="padding:8px;background-color:#E3E5ED; width:75%" class="card mb-3 box-shadow">
      <div class="card-img-top myImages" id="konva-container-req-selected"></div>

          </div> </div>
            <div class="col-lg-8 col-md-8 col-8" style="margin-bottom:20px;text-align: center;vertical-align: middle;align-items: center;justify-content: center; display: flex;" >
                <p style="font-size:30px"><b>Requirements:</b> <i>"${query}"</i></p>
                </div>`
}


function aspectGUICard2(index, feature_text) {
  return `<div id="aspect-card-2" class="col-lg-4 col-md-6 col-6 col-sm-6" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED; width:75%;text-align: center;vertical-align: middle;align-items: center;" class="card mb-3 box-shadow">
      <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">${index}.</p>
      <div class="card-img-top myImages" id="konva-container-req-summary-${index}"></div>
            <p style="font-size:15px;font-weight:bold;text-align:center;margin-bottom:3px">"${feature_text}"</p>

          </div> </div>`;
}


function renderGUIReqSummaryModal(data) {
    currentGUIReqSummary.value = data;
    // Clear the top of modal first
    $("#row-selected-gui").children().remove();
    $("#row-selected-gui").append(selectedGUICard(data['selected_gui_id'], data['nlr_query']));
    // clear aspect guis next
    $("#row-aspect-guis").children().remove();
    for (var i = 0; i < data['aspect_guis'].length; i++) {
         $("#row-aspect-guis").append(aspectGUICard(i+1, data['aspect_guis'][i]['text']));
         addKonvaImageAndFeatureWithContainer(data['aspect_guis'][i]['gui_id'], data['aspect_guis'][i]['bounds'], 'konva-container-req-'+(i+1));
    }

    if (showGUIReqSummary.value) {
          $('#modal_box').modal('open');
    } else {
         setTimeout(function() {
            $('#btn-req-continue').click();
        }, 500);
    } 
}


function renderGUIReqSummaryModal2(data) {
    // Clear the top of modal first
    $("#row-selected-gui-gui-summary").children().remove();
    $("#row-selected-gui-gui-summary").append(selectedGUICard(data['selected_gui_id'], data['nlr_query']));
    $("#row-aspect-guis-gui-summary").children().remove();
    for (var i = 0; i < data['aspect_guis'].length; i++) {
         $("#row-aspect-guis-gui-summary").append(aspectGUICard2(i+1, data['aspect_guis'][i]['text']));
         addKonvaImageAndFeatureWithContainer2(data['aspect_guis'][i]['gui_id'], data['aspect_guis'][i]['bounds'], 'konva-container-req-summary-'+(i+1));
    }
     $('#modal_box_gui_summary').scrollTop(0);
     $('#modal_box_gui_summary').modal('open');
}


function addKonvaSelectedGUIEditedCopy(gui_id) {
  var guiIndex = 'gui_' + gui_id;
    var stage = new Konva.Stage({
        container: "konva-container-req-selected",
      });

    var layer = new Konva.Layer();

    var guiIndexImg = guiIndex + '_img';
    var guiNodeKonva = layerPlay.findOne(`#${guiIndex}`);
    var imgNodeKonva = layerPlay.findOne(`#${guiIndexImg}`);
    
    scalePlayer = 0.6
    updatedWidth = imgNodeKonva.getAttr('width') * scalePlayer
    updatedHeight = imgNodeKonva.getAttr('height') * scalePlayer
    var clonedGuiNodeKonva = guiNodeKonva.clone();
    clonedGuiNodeKonva.children.forEach((c) => {
        oldWidth = c.getAttr('width');
        oldHeight = c.getAttr('height');
        c.width(oldWidth*scalePlayer);
        c.height(oldHeight*scalePlayer);
        c.children.forEach((d) => {
                oldWidth = d.getAttr('width');
                oldHeight = d.getAttr('height');
                d.width(oldWidth*scalePlayer);
                d.height(oldHeight*scalePlayer);
                

            });

    });

        stage.width(updatedWidth);
        stage.height(updatedHeight);
    
        $('#konva-container-req-selected').width(updatedWidth).height(updatedHeight);


    layer.add(clonedGuiNodeKonva);
    var imgNodeKonvaCloned = layer.findOne(`#${guiIndexImg}`);
    imgNodeKonvaCloned.width(updatedWidth);
    imgNodeKonvaCloned.height(updatedHeight);
    stage.add(layer);
    layer.batchDraw();
    
}


function updateModalAdditionalRequirements(data) {
   $("#row-aspect-guis-summary").children().remove();
   for (var i = 0; i < data['aspect_guis'].length; i++) {
         $("#row-aspect-guis-summary").append(aspectGUICardSummary(i+1, data['aspect_guis'][i]['text']));
         addKonvaImageAndFeatureWithContainer(data['aspect_guis'][i]['gui_id'], data['aspect_guis'][i]['bounds'], 'konva-container-req-summary'+(i+1));
    }
}

function guiNodesCard(index, feature_text) {
  return `          <div class="col-lg-3 col-md-3 col-3" style="margin-bottom:20px">
      <div style="padding:8px;background-color:#E3E5ED; height:100%" class="card mb-3 box-shadow">
        <button id="btn-gui-summary" data-val="${index}">
      <img class="card-img-top myImages" id="myImg-1" src=  "${baseURL}/combined/${index}.jpg" draggable="true" alt="GUI ${index}">
</button>
          </div>  </div>`;
}



function updateModalGUINodes() {
       $("#row-selected-gui-summary").children().remove();
       for (var i = 0; i < guiNodes.length; i++) { 
            $("#row-selected-gui-summary").append(guiNodesCard(guiNodes[i]['summary']['selected_gui_id'], guiNodes[i]['summary']['nlr_query']));
       }
}

module.exports['renderGUIRankingData'] = renderGUIRankingData;
module.exports['renderExampleGUI'] = renderExampleGUI;
module.exports['renderExampleGUIWithFeature'] = renderExampleGUIWithFeature;
module.exports['renderGUIReqSummaryModal'] = renderGUIReqSummaryModal;
module.exports['updateModalAdditionalRequirements'] = updateModalAdditionalRequirements;
module.exports['updateModalGUINodes'] = updateModalGUINodes;
module.exports['renderGUIReqSummaryModal2'] = renderGUIReqSummaryModal2;
module.exports['renderFeatureRanking'] = renderFeatureRanking;
module.exports['addKonvaImageAndFeatureForSummaryRendering'] = addKonvaImageAndFeatureForSummaryRendering;
module.exports['addAspectGUIsForPDFSummary'] = addAspectGUIsForPDFSummary;
module.exports['renderGUIRankingDataForAnnotation'] = renderGUIRankingDataForAnnotation;
module.exports['renderGUIRankingDataForTopKFinalAnnotation'] = renderGUIRankingDataForTopKFinalAnnotation;
module.exports['renderTopKFeatureRanking'] = renderTopKFeatureRanking;
module.exports['renderGUIRankingDataReselect'] = renderGUIRankingDataReselect;