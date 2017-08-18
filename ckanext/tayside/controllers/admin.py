from ckan.controllers.admin import AdminController
from ckan.plugins import toolkit


class AdminController(AdminController):
    def manage_footer_logos(self):
        return toolkit.render('admin/tayside_manage_footer_logos.html')
