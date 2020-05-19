/* add-dataset-modal
*
* This JavaScript module handles showing/hiding the Add dataset modal.
*
*/


this.ckan.module('add-dataset-modal', function($) {
  'use strict';

  return {
    initialize: function() {
      $.proxyAll(this, /_on/)

      this.el.on('click', this._onAddDatasetClick)

      this.datasetModal = $('.add-dataset-modal')
      this.datasetModalBackdrop = $('.add-dataset-modal-backdrop')
      this.dismissButton = this.datasetModal.find('button[data-dismiss="modal"]')

      this.datasetModalBackdrop.on('click', this._onCloseModal)
      this.dismissButton.on('click', this._onCloseModal)
    },
    _onCloseModal: function(event) {
      this.datasetModal.hide()
      this.datasetModalBackdrop.hide()
    },
    _onAddDatasetClick: function(event) {
      this.datasetModal.show()
      this.datasetModalBackdrop.show()
    }
  }
})



// Bugfix for modal not working on IE //s
$(document).ready(function(){

  var isIE11 = !!navigator.userAgent.match(/Trident.*rv\:11\./);
  //alert(isIE11);
  if(isIE11) {
    $('.btn').click(function(){
      $('.add-dataset-modal').css('display','block');
      $('.add-dataset-modal-backdrop').css('display','block'); 
    });
  
    $('.close').click(function(){
      $('.add-dataset-modal').css('display','none');
      $('.add-dataset-modal-backdrop').css('display','none'); 
    });
  
    $('.add-dataset-modal-backdrop').click(function(){
      $(this).css('display','none'); 
      $('.add-dataset-modal').css('display','none');
    });
  }
  
});