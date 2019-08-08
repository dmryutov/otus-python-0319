Selectize.define('create_on_blur', function() {
    if (this.settings.mode !== 'multi')
        return;
    var self = this;
    this.onBlur = (function(e) {
        var original = self.onBlur;
        return function(e) {
            if (this.$control_input.val().trim() != '') {
                self.createItem(this.$control_input.val());
            }
            return original.apply(this, arguments);
        }
    })();
});