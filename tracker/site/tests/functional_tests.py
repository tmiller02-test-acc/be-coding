from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.contrib.auth import get_user_model
from webtest.app import AppError
from tracker.site.models import Project, Ticket


class TicketsViewTest(WebTest):

    csrf_checks = False

    def setUp(self):
        self.project_one = Project.objects.create(title="Project One")
        self.project_two = Project.objects.create(title="Project Two")
        self.user = get_user_model().objects.create_user(
            'user', 'user@example.com', 'password')
        self.ticket_one = Ticket.objects.create(
            title="Ticket One",
            project=self.project_one,
        )
        self.ticket_one.assignees.add(self.user)

    def test_update_ticket(self):
        response = self.app.get(
            reverse(
                'ticket-update',
                kwargs={
                    'project_id': self.project_one.id,
                    'ticket_id': self.ticket_one.id
                }),
            user=self.user
        )
        ticket_form = response.forms.get('ticket-form')
        ticket_form['title'] = 'New ticket title'
        ticket_form['description'] = 'New description'
        response = ticket_form.submit(user=self.user)
        # reload ticket from database
        self.ticket_one = Ticket.objects.get(id=self.ticket_one.id)
        self.assertEqual(self.ticket_one.title, 'New ticket title')
        self.assertEqual(self.ticket_one.description, 'New description')
        self.assertEqual(self.ticket_one.project, self.project_one)

    def test_cannot_update_invalid_project_id(self):
        """
        Entering an invalid project_id should raise a 404
        """
        with self.assertRaisesMessage(AppError, "Bad response: 404 NOT FOUND"):
            self.app.get(
                reverse(
                    'ticket-update',
                    kwargs={
                        'project_id': self.project_two.id,
                        'ticket_id': self.ticket_one.id
                    }),
                user=self.user
            )


class ProjectDetailViewTest(WebTest):

    csrf_checks = False

    def setUp(self):
        self.project = Project.objects.create(title="Project")
        self.user = get_user_model().objects.create_user(
            'user', 'user@example.com', 'password')

    def test_notify_no_tickets(self):
        response = self.app.get(
            reverse(
                'project-detail',
                kwargs={
                    'project_id': self.project.id,
                }),
            user=self.user
        )
        self.assertContains(
            response, 'No tickets have been created for this project')

    def test_notify_no_assignees(self):
        Ticket.objects.create(
            title="Ticket",
            project=self.project,
        )

        response = self.app.get(
            reverse(
                'project-detail',
                kwargs={
                    'project_id': self.project.id,
                }),
            user=self.user
        )
        self.assertNotContains(
            response, 'No tickets have been created for this project')
        self.assertContains(
            response, 'No assigned users')