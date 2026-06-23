import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  int _currentStep = 0;
  bool _isLoading = false;

  // Personal
  final _firstNameCtrl = TextEditingController();
  final _lastNameCtrl = TextEditingController();
  final _aboutMeCtrl = TextEditingController();
  String? _gender;
  DateTime? _dob;
  final _heightCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();
  String? _physicalStatus;
  String? _maritalStatus;
  String? _motherTongue;

  // Religious
  String? _religion;
  final _casteCtrl = TextEditingController();
  final _subCasteCtrl = TextEditingController();
  final _gothramCtrl = TextEditingController();
  bool _dosham = false;
  bool _willingIntercaste = false;

  // Professional
  String? _education;
  final _institutionCtrl = TextEditingController();
  final _occupationCtrl = TextEditingController();
  final _organizationCtrl = TextEditingController();
  final _incomeCtrl = TextEditingController();

  // Location
  final _countryCtrl = TextEditingController(text: 'India');
  String? _state;
  final _districtCtrl = TextEditingController();
  final _cityCtrl = TextEditingController();

  // Family
  final _fatherOccCtrl = TextEditingController();
  final _motherOccCtrl = TextEditingController();
  final _siblingsCtrl = TextEditingController();
  String? _familyValues;
  String? _familyType;

  // Lifestyle
  String? _eatingHabit;
  String? _smokingHabit;
  String? _drinkingHabit;

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);

    final data = <String, dynamic>{
      'first_name': _firstNameCtrl.text,
      'last_name': _lastNameCtrl.text,
      'about_me': _aboutMeCtrl.text,
      'gender': _gender,
      'date_of_birth': _dob?.toIso8601String().split('T').first,
      'height_cm': int.tryParse(_heightCtrl.text),
      'weight_kg': int.tryParse(_weightCtrl.text),
      'physical_status': _physicalStatus,
      'marital_status': _maritalStatus,
      'mother_tongue': _motherTongue,
      'religion': _religion,
      'caste': _casteCtrl.text,
      'sub_caste': _subCasteCtrl.text,
      'gothram': _gothramCtrl.text,
      'dosham': _dosham,
      'willing_intercaste': _willingIntercaste,
      'education': _education,
      'institution': _institutionCtrl.text,
      'occupation': _occupationCtrl.text,
      'organization': _organizationCtrl.text,
      'annual_income': _incomeCtrl.text,
      'country': _countryCtrl.text,
      'state': _state,
      'district': _districtCtrl.text,
      'city': _cityCtrl.text,
      'father_occupation': _fatherOccCtrl.text,
      'mother_occupation': _motherOccCtrl.text,
      'siblings': _siblingsCtrl.text,
      'family_values': _familyValues,
      'family_type': _familyType,
      'eating_habit': _eatingHabit,
      'smoking_habit': _smokingHabit,
      'drinking_habit': _drinkingHabit,
    };

    // Remove null/empty values
    data.removeWhere((key, value) => value == null || value.toString().isEmpty);

    try {
      await ApiService().updateProfile(data);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile saved successfully!')),
        );
        context.go('/profile');
      }
    } catch (e) {
      // Try create if update fails
      try {
        await ApiService().createProfile(data);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Profile created!')),
          );
          context.go('/profile');
        }
      } catch (e2) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e2')),
          );
        }
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _aboutMeCtrl.dispose();
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    _casteCtrl.dispose();
    _subCasteCtrl.dispose();
    _gothramCtrl.dispose();
    _institutionCtrl.dispose();
    _occupationCtrl.dispose();
    _organizationCtrl.dispose();
    _incomeCtrl.dispose();
    _countryCtrl.dispose();
    _districtCtrl.dispose();
    _cityCtrl.dispose();
    _fatherOccCtrl.dispose();
    _motherOccCtrl.dispose();
    _siblingsCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Profile'),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveProfile,
            child: _isLoading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Text('Save', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: Stepper(
          currentStep: _currentStep,
          onStepContinue: () {
            if (_currentStep < 5) {
              setState(() => _currentStep++);
            } else {
              _saveProfile();
            }
          },
          onStepCancel: () {
            if (_currentStep > 0) setState(() => _currentStep--);
          },
          onStepTapped: (step) => setState(() => _currentStep = step),
          steps: [
            // Step 1: Personal
            Step(
              title: const Text('Personal Information'),
              isActive: _currentStep >= 0,
              content: Column(
                children: [
                  TextFormField(
                    controller: _firstNameCtrl,
                    decoration: const InputDecoration(labelText: 'First Name*'),
                    validator: (v) =>
                        v == null || v.isEmpty ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _lastNameCtrl,
                    decoration: const InputDecoration(labelText: 'Last Name*'),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _gender,
                    decoration: const InputDecoration(labelText: 'Gender*'),
                    items: ['Male', 'Female']
                        .map((g) => DropdownMenuItem(value: g.toLowerCase(), child: Text(g)))
                        .toList(),
                    onChanged: (v) => setState(() => _gender = v),
                  ),
                  const SizedBox(height: 12),
                  ListTile(
                    title: Text(_dob == null
                        ? 'Select Date of Birth*'
                        : 'DOB: ${_dob!.day}/${_dob!.month}/${_dob!.year}'),
                    trailing: const Icon(Icons.calendar_today),
                    onTap: () async {
                      final date = await showDatePicker(
                        context: context,
                        initialDate: DateTime(2000),
                        firstDate: DateTime(1960),
                        lastDate: DateTime(2008),
                      );
                      if (date != null) setState(() => _dob = date);
                    },
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _heightCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: 'Height (cm)'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextFormField(
                          controller: _weightCtrl,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: 'Weight (kg)'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _maritalStatus,
                    decoration: const InputDecoration(labelText: 'Marital Status*'),
                    items: AppConstants.maritalStatuses
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _maritalStatus = v),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _motherTongue,
                    decoration: const InputDecoration(labelText: 'Mother Tongue'),
                    items: AppConstants.motherTongues
                        .map((l) => DropdownMenuItem(value: l, child: Text(l)))
                        .toList(),
                    onChanged: (v) => setState(() => _motherTongue = v),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _aboutMeCtrl,
                    maxLines: 3,
                    decoration: const InputDecoration(
                      labelText: 'About Me',
                      hintText: 'Tell us about yourself...',
                    ),
                  ),
                ],
              ),
            ),

            // Step 2: Religion
            Step(
              title: const Text('Religious Background'),
              isActive: _currentStep >= 1,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _religion,
                    decoration: const InputDecoration(labelText: 'Religion'),
                    items: AppConstants.religions
                        .map((r) => DropdownMenuItem(value: r, child: Text(r)))
                        .toList(),
                    onChanged: (v) => setState(() => _religion = v),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _casteCtrl,
                    decoration: const InputDecoration(labelText: 'Caste'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _subCasteCtrl,
                    decoration: const InputDecoration(labelText: 'Sub Caste'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _gothramCtrl,
                    decoration: const InputDecoration(labelText: 'Gothram'),
                  ),
                  const SizedBox(height: 12),
                  SwitchListTile(
                    title: const Text('Dosham'),
                    value: _dosham,
                    onChanged: (v) => setState(() => _dosham = v),
                  ),
                  SwitchListTile(
                    title: const Text('Willing for Intercaste Marriage'),
                    value: _willingIntercaste,
                    onChanged: (v) => setState(() => _willingIntercaste = v),
                  ),
                ],
              ),
            ),

            // Step 3: Professional
            Step(
              title: const Text('Professional Details'),
              isActive: _currentStep >= 2,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _education,
                    decoration: const InputDecoration(labelText: 'Education'),
                    items: AppConstants.educationLevels
                        .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                        .toList(),
                    onChanged: (v) => setState(() => _education = v),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _institutionCtrl,
                    decoration: const InputDecoration(labelText: 'Institution'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _occupationCtrl,
                    decoration: const InputDecoration(labelText: 'Occupation'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _organizationCtrl,
                    decoration: const InputDecoration(labelText: 'Organization'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _incomeCtrl,
                    decoration: const InputDecoration(labelText: 'Annual Income'),
                  ),
                ],
              ),
            ),

            // Step 4: Location
            Step(
              title: const Text('Location'),
              isActive: _currentStep >= 3,
              content: Column(
                children: [
                  TextFormField(
                    controller: _countryCtrl,
                    decoration: const InputDecoration(labelText: 'Country'),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _state,
                    decoration: const InputDecoration(labelText: 'State'),
                    items: AppConstants.indianStates
                        .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _state = v),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _districtCtrl,
                    decoration: const InputDecoration(labelText: 'District'),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _cityCtrl,
                    decoration: const InputDecoration(labelText: 'City'),
                  ),
                ],
              ),
            ),

            // Step 5: Family
            Step(
              title: const Text('Family Details'),
              isActive: _currentStep >= 4,
              content: Column(
                children: [
                  TextFormField(
                    controller: _fatherOccCtrl,
                    decoration:
                        const InputDecoration(labelText: "Father's Occupation"),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _motherOccCtrl,
                    decoration:
                        const InputDecoration(labelText: "Mother's Occupation"),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _siblingsCtrl,
                    decoration: const InputDecoration(
                        labelText: 'Siblings (e.g., 1 Brother, 2 Sisters)'),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _familyValues,
                    decoration: const InputDecoration(labelText: 'Family Values'),
                    items: ['Traditional', 'Moderate', 'Liberal']
                        .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                        .toList(),
                    onChanged: (v) => setState(() => _familyValues = v),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _familyType,
                    decoration: const InputDecoration(labelText: 'Family Type'),
                    items: ['Joint', 'Nuclear']
                        .map((v) => DropdownMenuItem(value: v, child: Text(v)))
                        .toList(),
                    onChanged: (v) => setState(() => _familyType = v),
                  ),
                ],
              ),
            ),

            // Step 6: Lifestyle
            Step(
              title: const Text('Lifestyle'),
              isActive: _currentStep >= 5,
              content: Column(
                children: [
                  DropdownButtonFormField<String>(
                    value: _eatingHabit,
                    decoration: const InputDecoration(labelText: 'Eating Habits'),
                    items: AppConstants.eatingHabits
                        .map((e) => DropdownMenuItem(value: e.toLowerCase(), child: Text(e)))
                        .toList(),
                    onChanged: (v) => setState(() => _eatingHabit = v),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _smokingHabit,
                    decoration: const InputDecoration(labelText: 'Smoking'),
                    items: ['No', 'Occasionally', 'Yes']
                        .map((s) => DropdownMenuItem(value: s.toLowerCase(), child: Text(s)))
                        .toList(),
                    onChanged: (v) => setState(() => _smokingHabit = v),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _drinkingHabit,
                    decoration: const InputDecoration(labelText: 'Drinking'),
                    items: ['No', 'Occasionally', 'Yes']
                        .map((d) => DropdownMenuItem(value: d.toLowerCase(), child: Text(d)))
                        .toList(),
                    onChanged: (v) => setState(() => _drinkingHabit = v),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
