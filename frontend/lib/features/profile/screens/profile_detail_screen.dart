import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class ProfileDetailScreen extends StatefulWidget {
  final String userId;
  const ProfileDetailScreen({super.key, required this.userId});

  @override
  State<ProfileDetailScreen> createState() => _ProfileDetailScreenState();
}

class _ProfileDetailScreenState extends State<ProfileDetailScreen> {
  Map<String, dynamic>? _profile;
  bool _isLoading = true;
  bool _interestSent = false;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final response = await ApiService().getProfile(widget.userId);
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

  Future<void> _sendInterest() async {
    try {
      await ApiService().sendInterest(widget.userId,
          message: 'I am interested in your profile');
      if (mounted) {
        setState(() => _interestSent = true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Interest sent successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send interest: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(_profile?['display_name'] ?? 'Profile')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _profile == null
              ? const Center(child: Text('Profile not found'))
              : SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header
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
                              _profile!['display_name'] ?? '',
                              style: Theme.of(context)
                                  .textTheme
                                  .headlineSmall
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            if (_profile!['age'] != null)
                              Text(
                                '${_profile!['age']} yrs | ${_profile!['city'] ?? ''}, ${_profile!['state'] ?? ''}',
                              ),
                            if (_profile!['compatibility_score'] != null)
                              Chip(
                                label: Text(
                                  '${_profile!['compatibility_score']}% Compatible',
                                  style: const TextStyle(color: Colors.white),
                                ),
                                backgroundColor: AppTheme.primaryColor,
                              ),
                          ],
                        ),
                      ),

                      // About
                      if (_profile!['about_me'] != null)
                        Padding(
                          padding: const EdgeInsets.all(16),
                          child: Card(
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('About',
                                      style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 16)),
                                  const SizedBox(height: 8),
                                  Text(_profile!['about_me']),
                                ],
                              ),
                            ),
                          ),
                        ),

                      // Details grid
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            if (_profile!['education'] != null)
                              _DetailChip(Icons.school, _profile!['education']),
                            if (_profile!['occupation'] != null)
                              _DetailChip(Icons.work, _profile!['occupation']),
                            if (_profile!['religion'] != null)
                              _DetailChip(
                                  Icons.temple_hindu, _profile!['religion']),
                            if (_profile!['caste'] != null)
                              _DetailChip(Icons.people, _profile!['caste']),
                            if (_profile!['mother_tongue'] != null)
                              _DetailChip(
                                  Icons.language, _profile!['mother_tongue']),
                            if (_profile!['marital_status'] != null)
                              _DetailChip(Icons.favorite,
                                  _profile!['marital_status']),
                            if (_profile!['height_cm'] != null)
                              _DetailChip(
                                  Icons.height, '${_profile!['height_cm']} cm'),
                            if (_profile!['annual_income'] != null)
                              _DetailChip(Icons.currency_rupee,
                                  _profile!['annual_income']),
                          ],
                        ),
                      ),
                      const SizedBox(height: 80),
                    ],
                  ),
                ),
      bottomSheet: _profile != null
          ? Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).scaffoldBackgroundColor,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => context.push('/ai-assistant'),
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('AI Compatibility'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _interestSent ? null : _sendInterest,
                      icon: Icon(
                          _interestSent ? Icons.check : Icons.favorite),
                      label: Text(
                          _interestSent ? 'Interest Sent' : 'Send Interest'),
                    ),
                  ),
                ],
              ),
            )
          : null,
    );
  }
}

class _DetailChip extends StatelessWidget {
  final IconData icon;
  final String label;
  const _DetailChip(this.icon, this.label);

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 16),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      visualDensity: VisualDensity.compact,
    );
  }
}
