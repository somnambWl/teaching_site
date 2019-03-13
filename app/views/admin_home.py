#!/usr/bin/env python

from flask_admin import AdminIndexView, expose

# Import app
from app import app, db
from app.common.tables import create_summary_table

class HomeView(AdminIndexView):
    """

    """

    @expose('/')
    def index(self):
        table = create_summary_table()
        if table is not None:
            # Convert to HTML and specify class so the style of tables is uniform
            html_table = table.to_html(classes="table table-striped " \
                    "table-bordered table-hover model-list")
            return self.render('admin/home.html', table=html_table)
        return self.render('admin/home.html')
        
