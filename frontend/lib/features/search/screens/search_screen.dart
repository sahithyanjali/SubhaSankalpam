import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/constants/app_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  List<dynamic> _results = [];
  bool _isLoading = false;
  bool _showFilters = true;

  // Filter values
  RangeValues _ageRange = const RangeValues(21, 35);
  RangeValues _heightRange = const RangeValues(150, 185);
  String? _religion;
  String? _caste;
  String? _education;
  String? _maritalStatus;
  String? _state;
  String? _motherTongue;

  Future<void> _search() async {
    setState(() {
      _isLoading = true;
      _showFilters = false;
    });
    try {
      final filters = <String, dynamic>{
        'min_age': _ageRange.start.round(),
        'max_age': _ageRange.end.round(),
        'min_height': _heightRange.start.round(),
        'max_height': _heightRange.end.round(),
      };
      if (_religion != null) filters['religion'] = _religion;
      if (_caste != null) filters['caste'] = _caste;
      if (_education != null) filters['education'] = _education;
      if (_maritalStatus != null) filters['marital_status'] = _maritalStatus;
      if (_state != null) filters['location'] = _state;
      if (_motherTongue != null) filters['mother_tongue'] = _motherTongue;

      final response = await ApiService().searchProfiles(filters);
      if (mounted) {
        setState(() {
          _results = response.data['profiles'] ?? [];
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Search Profiles'),
        actions: [
          IconButton(
            icon: Icon(_showFilters ? Icons.close : Icons.filter_list),
            onPressed: () => setState(() => _showFilters = !_showFilters),
          ),
        ],
      ),
      body: Column(
        children: [
          // Filters
          if (_showFilters)
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Age Range: ${_ageRange.start.round()} - ${_ageRange.end.round()}'),
                    RangeSlider(
                      values: _ageRange,
                      min: 18,
                      max: 60,
                      divisions: 42,
                      labels: RangeLabels(
                        _ageRange.start.round().toString(),
                        _ageRange.end.round().toString(),
                      ),
                      onChanged: (v) => setState(() => _ageRange = v),
                    ),
                    const SizedBox(height: 8),
                    Text('Height (cm): ${_heightRange.start.round()} - ${_heightRange.end.round()}'),
                    RangeSlider(
                      values: _heightRange,
                      min: 130,
                      max: 210,
                      divisions: 80,
                      labels: RangeLabels(
                        _heightRange.start.round().toString(),
                        _heightRange.end.round().toString(),
                      ),
                      onChanged: (v) => setState(() => _heightRange = v),
                    ),
                    const SizedBox(height: 12),
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
                      decoration: const InputDecoration(labelText: 'Caste'),
                      onChanged: (v) => _caste = v.isEmpty ? null : v,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _education,
                      decoration: const InputDecoration(labelText: 'Education'),
                      items: AppConstants.educationLevels
                          .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                          .toList(),
                      onChanged: (v) => setState(() => _education = v),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _maritalStatus,
                      decoration:
                          const InputDecoration(labelText: 'Marital Status'),
                      items: AppConstants.maritalStatuses
                          .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                          .toList(),
                      onChanged: (v) => setState(() => _maritalStatus = v),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _motherTongue,
                      decoration:
                          const InputDecoration(labelText: 'Mother Tongue'),
                      items: AppConstants.motherTongues
                          .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                          .toList(),
                      onChanged: (v) => setState(() => _motherTongue = v),
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
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _search,
                        icon: const Icon(Icons.search),
                        label: const Text('Search'),
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _results.isEmpty
                      ? const Center(child: Text('No results found. Try adjusting filters.'))
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _results.length,
                          itemBuilder: (context, index) {
                            final profile = _results[index];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor:
                                      AppTheme.primaryColor.withOpacity(0.1),
                                  child: const Icon(Icons.person,
                                      color: AppTheme.primaryColor),
                                ),
                                title: Text(
                                  profile['display_name'] ?? 'Profile',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text(
                                  '${profile['age'] ?? ''} yrs | ${profile['education'] ?? ''} | ${profile['city'] ?? ''}',
                                ),
                                trailing: const Icon(Icons.chevron_right),
                                onTap: () =>
                                    context.push('/profile/${profile['user_id']}'),
                              ),
                            );
                          },
                        ),
            ),
        ],
      ),
    );
  }
}
