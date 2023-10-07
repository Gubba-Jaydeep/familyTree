window.addEventListener('load', function() {
    console.log('All assets are loaded');
    var textInput = document.querySelector('#input_form');
    var inputWrap = textInput.parentElement ;
    var inputWidth = parseInt(getComputedStyle(inputWrap).width);
    var svgText = Snap('.line');
    var qCurve = inputWidth / 2;  // For correct curving on diff screen sizes
    var textPath = svgText.path("M0 0 " + inputWidth + " 0");
    var textDown = function(){
        textPath.animate({d:"M0 0 Q" + qCurve + " 40 " + inputWidth + " 0"},150,mina.easeout);
    };
    var textUp = function(){
      textPath.animate({d:"M0 0 Q" + qCurve + " -30 " + inputWidth + " 0"},150,mina.easeout);
    };
    var textSame = function(){
      textPath.animate({d:"M0 0 " + inputWidth + " 0"},200,mina.easein);
    };
    var textRun = function(){
      setTimeout(textDown, 200 );
      setTimeout(textUp, 400 );
      setTimeout(textSame, 600 );
    };

    (function(){
        textInput.addEventListener('focus', function(){
          var parentDiv = this.parentElement;
          parentDiv.classList.add('active');
          textRun();
          this.addEventListener('blur', function(){
            var rg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.]{3,9})+\.([A-Za-z]{2,4})$/;
            this.value == 0 ? parentDiv.classList.remove('active') : null;
            !rg.test(this.value) && this.value != 0 ?
             (parentDiv.classList.remove('valid'), parentDiv.classList.add('invalid'), parentDiv.style.transformOrigin="center")
             : rg.test(this.value) && this.value != 0 ?
            (parentDiv.classList.add('valid'), parentDiv.classList.remove('invalid'), parentDiv.style.transformOrigin="bottom") :null;
            });
         parentDiv.classList.remove('valid', 'invalid')
        });

temp1=""
temp2=""
$(document).on("change", ".input_file", function(event) {
    console.log('something happend')
  var file_data = event.target.files[0]; // Getting the properties of file from file field
  var current_path = window.location.pathname; // Getting the properties of file from file field
  console.log(file_data)
  var form_data = new FormData(); // Creating object of FormData class
  form_data.append("file", file_data) // Appending parameter named file with properties of file_field to form_data
  form_data.append("user_id", event.target.id.split('_')[2]) // Adding extra parameters to form_data
  form_data.append("current_path", current_path) // Adding extra parameters to form_data
  $.ajax({
    url: "/upload_avatar", // Upload Script
    dataType: 'script',
    cache: false,
    contentType: false,
    processData: false,
    data: form_data, // Setting the data attribute of ajax with file_data
    type: 'post',
    success: function(data) {
        console.log('all ok')
    }
  });

})

    })();






//    var element =  document.getElementById('card_requestor');
//    if (typeof(element) != 'undefined' && element != null){
//        for (let i = 1; i < 100; i++) {
//            card = document.getElementById('card_'+i);
//            if(typeof(card) != 'undefined' && card != null){
//                if (element.style[1] == 'left'){
//                    line = new LeaderLine(element, card, {dropShadow: true, color:'white', path:'grid', endPlugOutline:false})
//                } else if(element.style[1] == 'right'){
//                    line = new LeaderLine(card, element, {dropShadow: true, color:'white', path:'grid', endPlugOutline:false})
//                }
//            }
//            else{
//                break
//            }
//        }
//    }
})
