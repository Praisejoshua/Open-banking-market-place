 # Fix Registration IntegrityError: UNIQUE constraint on UserPreference.user_id

## Steps:

- [x] **Step 1:** Edit `apps/accounts/views.py` - Remove manual `UserPreference.objects.create(user=self.object)` from `RegisterView.form_valid()` to prevent duplicate creation with signal.
- [x] **Step 2:** UserPreference IntegrityError resolved. New username error identified.
- [ ] **Step 3:** If orphan data persists, cleanup DB via shell: Delete UserPreference without matching User.
- [x] **Step 1.5:** Edit apps/accounts/forms.py to auto-generate unique username in UserRegistrationForm.

**Current Status:** UserPreference fix complete. New issue: username UNIQUE constraint. Step 1.5: Fix UserRegistrationForm username generation. Orphan cleanup syntax fix: `UserPreference.objects.filter(user__isnull=True).delete()` and for Users: `User.objects.filter(is_active=False).delete()` if needed.
