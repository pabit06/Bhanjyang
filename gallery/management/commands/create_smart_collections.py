from django.core.management.base import BaseCommand
from gallery.models import GalleryImage, SmartCollection, AutoCategorizationRule
import random
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create sample smart collections and auto-categorization rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--populate-ai-data',
            action='store_true',
            help='Populate sample AI data for existing images',
        )

    def handle(self, *args, **options):
        if options['populate_ai_data']:
            self.populate_ai_data()
        
        self.create_smart_collections()
        self.create_auto_categorization_rules()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created smart collections and auto-categorization rules!')
        )

    def populate_ai_data(self):
        """Populate sample AI data for existing images"""
        self.stdout.write('Populating AI data for existing images...')
        
        # Sample AI data
        sample_tags = [
            ['meeting', 'office', 'business', 'professional'],
            ['team', 'group', 'people', 'collaboration'],
            ['event', 'celebration', 'party', 'social'],
            ['award', 'recognition', 'achievement', 'success'],
            ['community', 'outreach', 'volunteer', 'service'],
            ['building', 'architecture', 'facility', 'infrastructure'],
            ['nature', 'outdoor', 'landscape', 'environment'],
            ['technology', 'computer', 'digital', 'innovation'],
        ]
        
        sample_objects = [
            ['person', 'table', 'chair', 'laptop'],
            ['person', 'group', 'handshake', 'smile'],
            ['cake', 'balloon', 'decoration', 'crowd'],
            ['trophy', 'certificate', 'medal', 'ribbon'],
            ['volunteer', 'community', 'help', 'service'],
            ['building', 'window', 'door', 'structure'],
            ['tree', 'sky', 'grass', 'nature'],
            ['computer', 'screen', 'keyboard', 'technology'],
        ]
        
        sample_scenes = [
            'office meeting', 'team collaboration', 'social event',
            'award ceremony', 'community service', 'office building',
            'outdoor setting', 'technology workspace'
        ]
        
        sample_sentiments = [
            'positive', 'professional', 'celebratory', 'achievement',
            'community', 'formal', 'natural', 'innovative'
        ]
        
        images = GalleryImage.objects.filter(is_active=True)
        
        for i, image in enumerate(images):
            # Assign random AI data
            tag_set = random.choice(sample_tags)
            object_set = random.choice(sample_objects)
            scene = random.choice(sample_scenes)
            sentiment = random.choice(sample_sentiments)
            quality_score = round(random.uniform(0.6, 0.95), 2)
            
            # Generate AI description
            description = f"AI-generated description for {image.title}: A {sentiment} scene showing {', '.join(tag_set[:2])} with {', '.join(object_set[:2])}."
            
            # Update image with AI data
            image.ai_tags = tag_set
            image.ai_objects = object_set
            image.ai_scene_type = scene
            image.ai_sentiment = sentiment
            image.ai_description = description
            image.ai_quality_score = quality_score
            
            # Generate color palette
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
            image.ai_color_palette = random.sample(colors, 3)
            
            image.save()
            
            self.stdout.write(f'  Updated AI data for: {image.title}')
        
        self.stdout.write(f'Successfully updated AI data for {images.count()} images.')

    def create_smart_collections(self):
        """Create sample smart collections"""
        self.stdout.write('Creating smart collections...')
        
        collections_data = [
            {
                'name': 'Professional Meetings',
                'description': 'Images from office meetings and business gatherings',
                'ai_tags': ['meeting', 'office', 'business'],
                'ai_objects': ['person', 'table', 'laptop'],
                'ai_scene_type': 'office meeting',
                'ai_sentiment': 'professional',
                'min_quality_score': 0.7,
                'is_featured': True,
            },
            {
                'name': 'Team Collaboration',
                'description': 'Images showing team work and collaboration',
                'ai_tags': ['team', 'group', 'people'],
                'ai_objects': ['person', 'group', 'handshake'],
                'ai_scene_type': 'team collaboration',
                'ai_sentiment': 'positive',
                'min_quality_score': 0.6,
                'is_featured': True,
            },
            {
                'name': 'Celebrations & Events',
                'description': 'Images from celebrations, parties, and social events',
                'ai_tags': ['event', 'celebration', 'party'],
                'ai_objects': ['cake', 'balloon', 'decoration'],
                'ai_scene_type': 'social event',
                'ai_sentiment': 'celebratory',
                'min_quality_score': 0.5,
                'is_featured': False,
            },
            {
                'name': 'Awards & Recognition',
                'description': 'Images from award ceremonies and recognition events',
                'ai_tags': ['award', 'recognition', 'achievement'],
                'ai_objects': ['trophy', 'certificate', 'medal'],
                'ai_scene_type': 'award ceremony',
                'ai_sentiment': 'achievement',
                'min_quality_score': 0.8,
                'is_featured': True,
            },
            {
                'name': 'Community Service',
                'description': 'Images from community outreach and volunteer activities',
                'ai_tags': ['community', 'outreach', 'volunteer'],
                'ai_objects': ['volunteer', 'community', 'help'],
                'ai_scene_type': 'community service',
                'ai_sentiment': 'community',
                'min_quality_score': 0.6,
                'is_featured': False,
            },
        ]
        
        for collection_data in collections_data:
            collection, created = SmartCollection.objects.get_or_create(
                name=collection_data['name'],
                defaults=collection_data
            )
            
            if created:
                self.stdout.write(f'  Created collection: {collection.name}')
                # Update the collection with matching images
                collection.update_collection()
            else:
                self.stdout.write(f'  Collection already exists: {collection.name}')

    def create_auto_categorization_rules(self):
        """Create sample auto-categorization rules"""
        self.stdout.write('Creating auto-categorization rules...')
        
        rules_data = [
            {
                'name': 'Office Meetings Rule',
                'description': 'Automatically categorize office meeting images',
                'ai_tags': ['meeting', 'office'],
                'ai_scene_type': 'office meeting',
                'target_category': 'office',
                'priority': 10,
                'is_active': True,
            },
            {
                'name': 'Team Photos Rule',
                'description': 'Automatically categorize team and group photos',
                'ai_tags': ['team', 'group', 'people'],
                'ai_objects': ['person', 'group'],
                'target_category': 'team',
                'priority': 9,
                'is_active': True,
            },
            {
                'name': 'Event Photos Rule',
                'description': 'Automatically categorize event and celebration photos',
                'ai_tags': ['event', 'celebration'],
                'ai_objects': ['cake', 'balloon', 'decoration'],
                'target_category': 'events',
                'priority': 8,
                'is_active': True,
            },
            {
                'name': 'Award Photos Rule',
                'description': 'Automatically categorize award and recognition photos',
                'ai_tags': ['award', 'recognition'],
                'ai_objects': ['trophy', 'certificate'],
                'target_category': 'awards',
                'priority': 7,
                'is_active': True,
                'mark_featured': True,
            },
            {
                'name': 'Community Photos Rule',
                'description': 'Automatically categorize community service photos',
                'ai_tags': ['community', 'volunteer'],
                'ai_objects': ['volunteer', 'community'],
                'target_category': 'community',
                'priority': 6,
                'is_active': True,
            },
            {
                'name': 'High Quality Photos Rule',
                'description': 'Mark high-quality photos as featured',
                'min_quality_score': 0.9,
                'target_category': 'events',
                'priority': 5,
                'is_active': True,
                'mark_featured': True,
            },
        ]
        
        for rule_data in rules_data:
            rule, created = AutoCategorizationRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            
            if created:
                self.stdout.write(f'  Created rule: {rule.name}')
            else:
                self.stdout.write(f'  Rule already exists: {rule.name}')
        
        self.stdout.write('Auto-categorization rules created successfully!')
