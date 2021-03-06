/* tayside-validate-resource
*
* This JavaScript module prepares the resource form for validating a resource.
*
*/

this.ckan.module('tayside-validate-resource', function($) {
  'use strict';

  return {
    initialize: function() {
      $.proxyAll(this, /_on/)

      this.checked = false
      this.resourceForm = $('#resource-edit')
      this.stagesContainer = $('.stages')
      this.el.on('click', this._onClick)
      this.validateStage = '<li><span>Validate resource</span></li>'
      this.buttonAgain = $('button[value="again"]')
      this.buttonFinish = $('button[value="go-metadata"]')
      this.buttonPrevious = $('button[value="go-dataset"]')
    },
    _onClick: function(event) {
      var validate = ''
      this.checked = !this.checked

      if (this.checked) {
        validate = '/validate'
        this.stagesContainer.addClass('validate-resource')
        this.stagesContainer.append(this.validateStage)
        this.buttonAgain.hide()
        this.buttonFinish.text('Next: Validate resource')
        this.buttonPrevious.attr('onclick', 'window.history.back()')
      } else {
        this.stagesContainer.removeClass('validate-resource')
        this.stagesContainer.children().last().remove()
        this.buttonAgain.show()
        this.buttonFinish.text('Finish')
        this.buttonPrevious.removeAttr('onclick')
      }

      this.resourceForm.attr('action', '/dataset/new_resource/' + this.options.pkg_name + validate)
    }
  }
})
