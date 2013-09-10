# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from elections.models import CandidatePerson, Election
from candideitorg.models import Candidate as CanCandidate, Election as CanElection
from django.utils.unittest import skip
from popit.models import Person, ApiInstance as PopitApiInstance
from django.db import IntegrityError
from django.conf import settings
import simplejson as json
import urllib
import re
from popit.tests.instance_helpers import delete_api_database


class CandideitorCandideitPopitPerson(TestCase):
    def setUp(self):
        super(CandideitorCandideitPopitPerson, self).setUp()
        self.pedro = Person.objects.get(name="Pedro")
        self.marcel = Person.objects.get(name="Marcel")
        self.candidato1 = CanCandidate.objects.get(id=1)
        self.candidato2 = CanCandidate.objects.get(id=2)

    def test_create_a_model_that_relates_them_both(self):
        candidate_person = CandidatePerson.objects.create(
            person=self.pedro,
            candidate=self.candidato1
            )

        self.assertEquals(candidate_person.person, self.pedro)
        self.assertEquals(candidate_person.candidate, self.candidato1)

        self.assertEquals(self.pedro.relation, candidate_person)
        self.assertEquals(self.candidato1.relation, candidate_person)



class AutomaticCreationOfThingsWhenLoadingCandideitorgs(TestCase):
    #Ya se que esto está terrible de mal escrito por que no describe niuna wea
    #pero la idea es que cuando se cree una elección del candideitorg, que viene desde 
    #el django candideitorg se creen elecciones del votainteligente
    #y además se cree un popit API instance
    #Si a alguien se le ocurre un mejor nombre que lo cambie!
    def setUp(self):
        super(AutomaticCreationOfThingsWhenLoadingCandideitorgs, self).setUp()


    def test_it_creates_an_election_out_of_a_candideitorg_election(self):
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        election = Election.objects.get(can_election=can_election)
        
        self.assertIsNotNone(election)
        self.assertEquals(election.name, can_election.name)
        self.assertEquals(election.description, can_election.description)

    #ya se me ocurrió wn!!
    def test_it_only_creates_one(self):
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        can_election.save()

        self.assertEquals(Election.objects.filter(can_election=can_election).count(), 1)

        election = Election.objects.get(can_election=can_election)
        self.assertTrue(election)

    def test_can_election_to_election_is_one_to_one(self):
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

        #ok it now has a relation between a can_election and an election
        #if I try add another one it should simply throw an integrity error

        with self.assertRaises(IntegrityError) as e:
            Election.objects.create(
                    description = can_election.description,
                    can_election=can_election,
                    name = can_election.name,
                    )


    def test_election_can_election_related_name(self):
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )


        election = Election.objects.get(can_election=can_election)
        self.assertEquals(can_election.election, election)

    def test_it_creates_a_popit_API_client(self):
        can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )
        #Create one ApiInstance for the love of the FSM

        self.assertIsNotNone(can_election.election.popit_api_instance)
        #manso webeo pa llegar a la APIinstance

        api_instance = can_election.election.popit_api_instance
        expected_url = "http://%s.%s.xip.io:%s/api" % ( can_election.election.slug,
                                                      settings.TEST_POPIT_API_HOST_IP,
                                                      settings.TEST_POPIT_API_PORT )
        self.assertEquals(api_instance.url, expected_url)


class AutomaticCreationOfAPopitPerson(TestCase):
    def setUp(self):
        super(AutomaticCreationOfAPopitPerson, self).setUp()
        self.can_election = CanElection.objects.create(
            description = "Elecciones CEI 2012",
            remote_id = 1,
            information_source = "",
            logo = "/media/photos/dummy.jpg",
            name = "cei 2012",
            resource_uri = "/api/v2/election/1/",
            slug = "cei-2012",
            use_default_media_naranja_option = True
            )

    def tearDown(self):
        super(AutomaticCreationOfAPopitPerson, self).tearDown()
        delete_api_database()


    def test_when_creating_a_candidate_it_creates_a_person(self):
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=self.can_election
            )

        self.assertIsNotNone(can_candidate.relation)
        self.assertEquals(can_candidate.relation.person.name, can_candidate.name)
        self.assertEquals(can_candidate.relation.person.api_instance.election, self.can_election.election)


    def test_it_does_not_create_two_relations(self):
        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=self.can_election
            )
        can_candidate.save()

        self.assertTrue(can_candidate.relation)

    def test_it_posts_to_the_popit_api(self):
        

        can_candidate = CanCandidate.objects.create(
            remote_id=1,
            resource_uri="/api/v2/candidate/1/",
            name="Perico los Palotes",
            election=self.can_election
            )

        person = can_candidate.relation.person
        instance = person.api_instance
        my_re = re.compile(instance.url + "/persons/([^/]+)/{0,1}")
        self.assertIsNotNone(my_re.match(person.popit_url))

        person_id = my_re.match(person.popit_url).groups()[0]
        response = urllib.urlopen(person.popit_url)
        self.assertEquals(response.code, 200)
        response_as_json = json.loads(response.read())

