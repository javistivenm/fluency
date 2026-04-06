from django.contrib import admin

from .models import Constraint, ConstraintType, DailyChallenge, Exercise, ExerciseConstraint, ExerciseType, Level, OutputFormat, Topic


class ExerciseConstraintInline(admin.TabularInline):
    model = ExerciseConstraint
    extra = 1


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    search_fields = ('code', 'name')


@admin.register(OutputFormat)
class OutputFormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'default_output_format', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')


@admin.register(ConstraintType)
class ConstraintTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Constraint)
class ConstraintAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'constraint_type', 'is_active')
    list_filter = ('level', 'constraint_type', 'is_active')
    search_fields = ('name', 'slug', 'description')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'exercise_type', 'topic', 'difficulty_score', 'is_active')
    list_filter = ('level', 'exercise_type', 'topic', 'is_active')
    search_fields = ('title', 'instructions', 'pedagogical_goal', 'grammar_focus', 'writing_function')
    inlines = (ExerciseConstraintInline,)


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('challenge_date', 'level', 'exercise', 'created_at')
    list_filter = ('challenge_date', 'level')
    date_hierarchy = 'challenge_date'
    search_fields = ('exercise__title',)
