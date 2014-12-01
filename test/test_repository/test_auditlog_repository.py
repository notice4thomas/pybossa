# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2014 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.
# Cache global variables for timeouts

from default import Test, db
from nose.tools import assert_raises
from factories import AppFactory
from factories import AuditlogFactory, UserFactory
from pybossa.repositories import AuditlogRepository
from pybossa.exc import WrongObjectError, DBIntegrityError


class TestAuditlogRepositoryForProjects(Test):

    def setUp(self):
        super(TestAuditlogRepositoryForProjects, self).setUp()
        self.auditlog_repo = AuditlogRepository(db)


    def test_get_return_none_if_no_log(self):
        """Test get method returns None if there is no log with the
        specified id"""

        log = self.auditlog_repo.get(2)

        assert log is None, log


    def test_get_returns_log(self):
        """Test get method returns a log if exists"""

        app = AppFactory.create()
        log = AuditlogFactory.create(app_id=app.id,
                                     app_short_name=app.short_name,
                                     user_id=app.owner.id,
                                     user_name=app.owner.name)

        retrieved_log = self.auditlog_repo.get(log.id)

        assert log == retrieved_log, retrieved_log


    def test_get_by(self):
        """Test get_by returns a log with the specified attribute"""

        app = AppFactory.create()
        log = AuditlogFactory.create(app_id=app.id,
                                     app_short_name=app.short_name,
                                     user_id=app.owner.id,
                                     user_name=app.owner.name)


        retrieved_log = self.auditlog_repo.get_by(user_id=app.owner.id)

        assert log == retrieved_log, retrieved_log


    def test_get_by_returns_none_if_no_log(self):
        """Test get_by returns None if no log matches the query"""

        app = AppFactory.create()
        AuditlogFactory.create(app_id=app.id,
                               app_short_name=app.short_name,
                               user_id=app.owner.id,
                               user_name=app.owner.name)

        retrieved_log = self.auditlog_repo.get_by(user_id=5555)

        assert retrieved_log is None, retrieved_log


    def test_filter_by_no_matches(self):
        """Test filter_by returns an empty list if no log matches the query"""

        app = AppFactory.create()
        AuditlogFactory.create(app_id=app.id,
                               app_short_name=app.short_name,
                               user_id=app.owner.id,
                               user_name=app.owner.name)

        retrieved_logs = self.auditlog_repo.filter_by(user_name='no_name')

        assert isinstance(retrieved_logs, list)
        assert len(retrieved_logs) == 0, retrieved_logs


    def test_filter_by_one_condition(self):
        """Test filter_by returns a list of logs that meet the filtering
        condition"""

        app = AppFactory.create()
        AuditlogFactory.create_batch(size=3, app_id=app.id,
                               app_short_name=app.short_name,
                               user_id=app.owner.id,
                               user_name=app.owner.name)

        app2 = AppFactory.create()
        should_be_missing = AuditlogFactory.create_batch(size=3, app_id=app2.id,
                                                   app_short_name=app2.short_name,
                                                   user_id=app2.owner.id,
                                                   user_name=app2.owner.name)


        retrieved_logs = self.auditlog_repo.filter_by(user_id=app.owner.id)

        assert len(retrieved_logs) == 3, retrieved_logs
        assert should_be_missing not in retrieved_logs, retrieved_logs


    def test_filter_by_multiple_conditions(self):
        """Test filter_by supports multiple-condition queries"""

        app = AppFactory.create()
        user = UserFactory.create()
        AuditlogFactory.create_batch(size=3, app_id=app.id,
                               app_short_name=app.short_name,
                               user_id=app.owner.id,
                               user_name=app.owner.name)

        log = AuditlogFactory.create(app_id=app.id,
                                     app_short_name=app.short_name,
                                     user_id=user.id,
                                     user_name=user.name)

        retrieved_logs = self.auditlog_repo.filter_by(app_id=app.id,
                                                      user_id=user.id)

        assert len(retrieved_logs) == 1, retrieved_logs
        assert log in retrieved_logs, retrieved_logs


    def test_save(self):
        """Test save persist the log"""

        app = AppFactory.create()
        log = AuditlogFactory.build(app_id=app.id,
                                    app_short_name=app.short_name,
                                    user_id=app.owner.id,
                                    user_name=app.owner.name)

        assert self.auditlog_repo.get(log.id) is None

        self.auditlog_repo.save(log)

        assert self.auditlog_repo.get(log.id) == log, "Log not saved"


    def test_save_fails_if_integrity_error(self):
        """Test save raises a DBIntegrityError if the instance to be saved lacks
        a required value"""

        log = AuditlogFactory.build()

        assert_raises(DBIntegrityError, self.auditlog_repo.save, log)


    #def test_save_only_saves_projects(self):
    #    """Test save raises a WrongObjectError when an object which is not
    #    a Project (App) instance is saved"""

    #    bad_object = dict()

    #    assert_raises(WrongObjectError, self.project_repo.save, bad_object)


    #def test_update(self):
    #    """Test update persists the changes made to the project"""

    #    project = AppFactory.create(description='this is a project')
    #    project.description = 'the description has changed'

    #    self.project_repo.update(project)
    #    updated_project = self.project_repo.get(project.id)

    #    assert updated_project.description == 'the description has changed', updated_project


    #def test_update_fails_if_integrity_error(self):
    #    """Test update raises a DBIntegrityError if the instance to be updated
    #    lacks a required value"""

    #    project = AppFactory.create()
    #    project.name = None

    #    assert_raises(DBIntegrityError, self.project_repo.update, project)


    #def test_update_only_updates_projects(self):
    #    """Test update raises a WrongObjectError when an object which is not
    #    a Project (App) instance is updated"""

    #    bad_object = dict()

    #    assert_raises(WrongObjectError, self.project_repo.update, bad_object)


    #def test_delete(self):
    #    """Test delete removes the project instance"""

    #    project = AppFactory.create()

    #    self.project_repo.delete(project)
    #    deleted = self.project_repo.get(project.id)

    #    assert deleted is None, deleted


    #def test_delete_also_removes_dependant_resources(self):
    #    """Test delete removes project tasks and taskruns too"""
    #    from factories import TaskFactory, TaskRunFactory, BlogpostFactory
    #    from pybossa.repositories import TaskRepository, BlogRepository

    #    project = AppFactory.create()
    #    task = TaskFactory.create(app=project)
    #    taskrun = TaskRunFactory.create(task=task)
    #    blogpost = BlogpostFactory.create(app=project)

    #    self.project_repo.delete(project)
    #    deleted_task = TaskRepository(db).get_task(task.id)
    #    deleted_taskrun = TaskRepository(db).get_task_run(taskrun.id)
    #    deleted_blogpost = BlogRepository(db).get(blogpost.id)

    #    assert deleted_task is None, deleted_task
    #    assert deleted_taskrun is None, deleted_taskrun


    #def test_delete_only_deletes_projects(self):
    #    """Test delete raises a WrongObjectError if is requested to delete other
    #    than a project"""

    #    bad_object = dict()

    #    assert_raises(WrongObjectError, self.project_repo.delete, bad_object)



#class TestProjectRepositoryForCategories(Test):

    #def setUp(self):
    #    super(TestProjectRepositoryForCategories, self).setUp()
    #    self.project_repo = ProjectRepository(db)


    #def test_get_category_return_none_if_no_category(self):
    #    """Test get_category method returns None if there is no category with
    #    the specified id"""

    #    category = self.project_repo.get_category(200)

    #    assert category is None, category


    #def test_get_category_returns_category(self):
    #    """Test get_category method returns a category if exists"""

    #    category = CategoryFactory.create()

    #    retrieved_category = self.project_repo.get_category(category.id)

    #    assert category == retrieved_category, retrieved_category


    #def test_get_category_by(self):
    #    """Test get_category returns a category with the specified attribute"""

    #    category = CategoryFactory.create(name='My Cat', short_name='mycat')

    #    retrieved_category = self.project_repo.get_category_by(name=category.name)

    #    assert category == retrieved_category, retrieved_category


    #def test_get_category_by_returns_none_if_no_category(self):
    #    """Test get_category returns None if no category matches the query"""

    #    CategoryFactory.create(name='My Project', short_name='mycategory')

    #    category = self.project_repo.get_by(name='no_name')

    #    assert category is None, category


    #def get_all_returns_list_of_all_categories(self):
    #    """Test get_all_categories returns a list of all the existing categories"""

    #    categories = CategoryFactory.create_batch(3)

    #    retrieved_categories = self.project_repo.get_all_categories()

    #    assert isinstance(retrieved_categories, list)
    #    assert len(retrieved_categories) == len(categories), retrieved_categories
    #    for category in retrieved_categories:
    #        assert category in categories, category


    #def test_filter_categories_by_no_matches(self):
    #    """Test filter_categories_by returns an empty list if no categories
    #    match the query"""

    #    CategoryFactory.create(name='My Project', short_name='mycategory')

    #    retrieved_categories = self.project_repo.filter_categories_by(name='no_name')

    #    assert isinstance(retrieved_categories, list)
    #    assert len(retrieved_categories) == 0, retrieved_categories


    #def test_filter_categories_by_one_condition(self):
    #    """Test filter_categories_by returns a list of categories that meet
    #    the filtering condition"""

    #    CategoryFactory.create_batch(3, description='generic category')
    #    should_be_missing = CategoryFactory.create(description='other category')

    #    retrieved_categories = (self.project_repo
    #        .filter_categories_by(description='generic category'))

    #    assert len(retrieved_categories) == 3, retrieved_categories
    #    assert should_be_missing not in retrieved_categories, retrieved_categories


    #def test_filter_categories_by_limit_offset(self):
    #    """Test that filter_categories_by supports limit and offset options"""

    #    CategoryFactory.create_batch(4)
    #    all_categories = self.project_repo.filter_categories_by()

    #    first_two = self.project_repo.filter_categories_by(limit=2)
    #    last_two = self.project_repo.filter_categories_by(limit=2, offset=2)

    #    assert len(first_two) == 2, first_two
    #    assert len(last_two) == 2, last_two
    #    assert first_two == all_categories[:2]
    #    assert last_two == all_categories[2:]


    #def test_save_category(self):
    #    """Test save_category persist the category"""

    #    category = CategoryFactory.build()
    #    assert self.project_repo.get(category.id) is None

    #    self.project_repo.save_category(category)

    #    assert self.project_repo.get_category(category.id) == category, "Category not saved"


    #def test_save_category_fails_if_integrity_error(self):
    #    """Test save_category raises a DBIntegrityError if the instance to be
    #   saved lacks a required value"""

    #    category = CategoryFactory.build(name=None)

    #    assert_raises(DBIntegrityError, self.project_repo.save_category, category)


    #def test_save_category_only_saves_categories(self):
    #    """Test save_category raises a WrongObjectError when an object which is
    #    not a Category instance is saved"""

    #    bad_object = AppFactory.build()

    #    assert_raises(WrongObjectError, self.project_repo.save_category, bad_object)


    #def test_update_category(self):
    #    """Test update_category persists the changes made to the category"""

    #    category = CategoryFactory.create(description='this is a category')
    #    category.description = 'the description has changed'

    #    self.project_repo.update_category(category)
    #    updated_category = self.project_repo.get_category(category.id)

    #    assert updated_category.description == 'the description has changed', updated_category


    #def test_update_category_fails_if_integrity_error(self):
    #    """Test update raises a DBIntegrityError if the instance to be updated
    #    lacks a required value"""

    #    category = CategoryFactory.create()
    #    category.name = None

    #    assert_raises(DBIntegrityError, self.project_repo.update_category, category)


    #def test_update_category_only_updates_categories(self):
    #    """Test update_category raises a WrongObjectError when an object which is
    #    not a Category instance is updated"""

    #    bad_object = AppFactory.build()

    #    assert_raises(WrongObjectError, self.project_repo.update_category, bad_object)


    #def test_delete_category(self):
    #    """Test delete_category removes the category instance"""

    #    category = CategoryFactory.create()

    #    self.project_repo.delete_category(category)
    #    deleted = self.project_repo.get_category(category.id)

    #    assert deleted is None, deleted


    #def test_delete_category_only_deletes_categories(self):
    #    """Test delete_category raises a WrongObjectError if is requested to
    #    delete other than a category"""

    #    bad_object = dict()

    #    assert_raises(WrongObjectError, self.project_repo.delete_category, bad_object)
