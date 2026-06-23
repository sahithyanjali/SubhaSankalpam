import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class MyProfileScreen extends StatefulWidget {
  const MyProfileScreen({super.key});

  @override
  State<MyProfileScreen> createState() => _MyProfileScreenState();
}

class _MyProfileScreenState extends State<MyProfileScreen> {
  Map<String, dynamic>? _profile;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final response = await ApiService().getMyProfile();
      if (mounted) {
        setState(() {
          _profile = response.data;
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
        title: const Text('My Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () => context.push('/edit-profile'),
          ),
          PopupMenuButton(
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'subscription', child: Text('My Subscription')),
              const PopupMenuItem(value: 'settings', child: Text('Settings')),
              const PopupMenuItem(value: 'logout', child: Text('Logout')),
            ],
            onSelected: (value) async {
              switch (value) {
                case 'subscription':
                  context.push('/subscriptions');
                case 'settings':
                  context.push('/settings');
                case 'logout':
                  await ApiService().clearTokens();
                  if (context.mounted) context.go('/login');
              }
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _profile == null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text('Profile not created yet'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () => context.push('/edit-profile'),
                        child: const Text('Create Profile'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadProfile,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    child: Column(
                      children: [
                        // Profile header
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                AppTheme.primaryColor.withOpacity(0.1),
                                AppTheme.secondaryColor.withOpacity(0.05),
                              ],
                            ),
                          ),
                          child: Column(
                            children: [
                              Stack(
                                children: [
                                  CircleAvatar(
                                    radius: 50,
                                    backgroundColor:
                                        AppTheme.primaryColor.withOpacity(0.2),
                                    child: const Icon(Icons.person,
                                        size: 50, color: AppTheme.primaryColor),
                                  ),
                                  if (_profile!['verified_badge'] == true)
                                    Positioned(
                                      bottom: 0,
                                      right: 0,
                                      child: Container(
                                        padding: const EdgeInsets.all(4),
                                        decoration: const BoxDecoration(
                                          color: Colors.white,
                                          shape: BoxShape.circle,
                                        ),
                                        child: const Icon(Icons.verified,
                                            color: Colors.blue, size: 24),
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 12),
                              Text(
                                _profile!['display_name'] ?? 'Your Name',
                                style: Theme.of(context)
                                    .textTheme
                                    .headlineSmall
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                              if (_profile!['age'] != null)
                                Text(
                                  '${_profile!['age']} yrs | ${_profile!['city'] ?? ''}, ${_profile!['state'] ?? ''}',
                                  style: Theme.of(context).textTheme.bodyMedium,
                                ),
                              const SizedBox(height: 8),
                              // Completeness
                              if (_profile!['profile_completeness'] != null)
                                Column(
                                  children: [
                                    Text(
                                      'Profile ${_profile!['profile_completeness']}% complete',
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                    const SizedBox(height: 4),
                                    LinearProgressIndicator(
                                      value: (_profile!['profile_completeness'] ?? 0) / 100,
                                      backgroundColor: Colors.grey.shade300,
                                      color: AppTheme.primaryColor,
                                    ),
                                  ],
                                ),
                            ],
                          ),
                        ),

                        // Profile sections
                        _ProfileSection(
                          title: 'Personal Information',
                          icon: Icons.person,
                          items: {
                            'Gender': _profile!['gender'],
                            'Date of Birth': _profile!['date_of_birth'],
                            'Height': _profile!['height_cm'] != null
                                ? '${_profile!['height_cm']} cm'
                                : null,
                            'Weight': _profile!['weight_kg'] != null
                                ? '${_profile!['weight_kg']} kg'
                                : null,
                            'Physical Status': _profile!['physical_status'],
                            'Marital Status': _profile!['marital_status'],
                            'Mother Tongue': _profile!['mother_tongue'],
                          },
                        ),
                        _ProfileSection(
                          title: 'Religious Background',
                          icon: Icons.temple_hindu,
                          items: {
                            'Religion': _profile!['religion'],
                            'Caste': _profile!['caste'],
                            'Sub Caste': _profile!['sub_caste'],
                            'Gothram': _profile!['gothram'],
                            'Dosham': _profile!['dosham']?.toString(),
                            'Willing for Intercaste':
                                _profile!['willing_intercaste']?.toString(),
                          },
                        ),
                        _ProfileSection(
                          title: 'Professional Details',
                          icon: Icons.work,
                          items: {
                            'Education': _profile!['education'],
                            'Institution': _profile!['institution'],
                            'Occupation': _profile!['occupation'],
                            'Organization': _profile!['organization'],
                            'Annual Income': _profile!['annual_income'],
                          },
                        ),
                        _ProfileSection(
                          title: 'Location',
                          icon: Icons.location_on,
                          items: {
                            'Country': _profile!['country'],
                            'State': _profile!['state'],
                            'District': _profile!['district'],
                            'City': _profile!['city'],
                          },
                        ),
                        _ProfileSection(
                          title: 'Family Details',
                          icon: Icons.family_restroom,
                          items: {
                            'Father Occupation': _profile!['father_occupation'],
                            'Mother Occupation': _profile!['mother_occupation'],
                            'Siblings': _profile!['siblings'],
                            'Family Values': _profile!['family_values'],
                            'Family Type': _profile!['family_type'],
                          },
                        ),
                        _ProfileSection(
                          title: 'Lifestyle',
                          icon: Icons.restaurant,
                          items: {
                            'Eating Habits': _profile!['eating_habit'],
                            'Smoking': _profile!['smoking_habit'],
                            'Drinking': _profile!['drinking_habit'],
                          },
                        ),
                        const SizedBox(height: 32),
                      ],
                    ),
                  ),
                ),
    );
  }
}

class _ProfileSection extends StatelessWidget {
  final String title;
  final IconData icon;
  final Map<String, dynamic?> items;

  const _ProfileSection({
    required this.title,
    required this.icon,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final nonNullItems =
        items.entries.where((e) => e.value != null && e.value.toString().isNotEmpty).toList();
    if (nonNullItems.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, size: 20, color: AppTheme.primaryColor),
                  const SizedBox(width: 8),
                  Text(title,
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 16)),
                ],
              ),
              const Divider(),
              ...nonNullItems.map((entry) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(
                          width: 140,
                          child: Text(entry.key,
                              style: const TextStyle(color: Colors.grey)),
                        ),
                        Expanded(
                          child: Text(entry.value.toString(),
                              style:
                                  const TextStyle(fontWeight: FontWeight.w500)),
                        ),
                      ],
                    ),
                  )),
            ],
          ),
        ),
      ),
    );
  }
}
