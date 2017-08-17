(function() {
  var imageUploadMacros = $('div[data-module="image-upload"]')

  // The image-upload module doesn't handle properly when multiple image modules
  // are present on the same page. Labels are the same for every module, and
  // ids of inputs as well.
  //
  // This code updates the labels and ids accordingly. It must be done after a
  // certain timeout otherwise won't work. It's race conditioning with
  // initialization of other modules.
  setTimeout(function() {
     $.each(imageUploadMacros, function(id, macro) {
      macro = $(macro)

      var labels = macro.find('label')
      var inputs = macro.find('input')
      var labelText = ''

      $.each(labels, function(id, label) {
        label = $(label)

        if (id === 0) {
          labelText = label.text()
        } else {
          label.text(labelText)
        }

        var labelForText= label.attr('for')
        var fieldText = ''

        if (labelForText === 'field-image-url') {
          fieldText = macro.attr('data-module-field_url')
        } else if (labelForText === 'field-image-upload') {
          fieldText = macro.attr('data-module-field_upload')
        }

        label.attr('for', fieldText)
      })

      $.each(inputs, function(id, input) {
        input = $(input)

        var inputId = input.attr('id')
        var fieldText = ''

        if (inputId === 'field-image-url') {
          fieldText = macro.attr('data-module-field_url')
        } else if (inputId === 'field-image-upload') {
          fieldText = macro.attr('data-module-field_upload')
        }

        input.attr('id', fieldText)
      })
    })
  }, 500)
})()
