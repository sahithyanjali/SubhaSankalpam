import 'package:flutter/material.dart';

import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class SubscriptionScreen extends StatefulWidget {
  const SubscriptionScreen({super.key});

  @override
  State<SubscriptionScreen> createState() => _SubscriptionScreenState();
}

class _SubscriptionScreenState extends State<SubscriptionScreen> {
  List<dynamic> _plans = [];
  Map<String, dynamic>? _currentSub;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final plansRes = await ApiService().getPlans();
      final subRes = await ApiService().getMySubscription();
      if (mounted) {
        setState(() {
          _plans = plansRes.data ?? [];
          _currentSub = subRes.data;
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _subscribe(String planId) async {
    try {
      await ApiService().subscribePlan(planId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Subscription activated!')),
        );
        _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Color _tierColor(String? tier) {
    switch (tier?.toLowerCase()) {
      case 'silver':
        return Colors.blueGrey;
      case 'gold':
        return const Color(0xFFDAA520);
      case 'platinum':
        return Colors.deepPurple;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Subscription Plans')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Current subscription
                  if (_currentSub != null)
                    Card(
                      color: AppTheme.primaryColor.withOpacity(0.05),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Current Plan',
                                style: TextStyle(
                                    fontWeight: FontWeight.bold, fontSize: 16)),
                            const SizedBox(height: 8),
                            Text(
                              _currentSub!['plan_name'] ?? 'Free',
                              style: Theme.of(context)
                                  .textTheme
                                  .headlineSmall
                                  ?.copyWith(
                                    color: AppTheme.primaryColor,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                            if (_currentSub!['expires_at'] != null)
                              Text('Expires: ${_currentSub!['expires_at']}'),
                          ],
                        ),
                      ),
                    ),
                  const SizedBox(height: 24),
                  Text('Choose a Plan',
                      style: Theme.of(context)
                          .textTheme
                          .titleLarge
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  ..._plans.map((plan) {
                    final tier = plan['tier']?.toString() ?? 'free';
                    final isCurrent = _currentSub?['plan_id'] == plan['id'];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                        side: isCurrent
                            ? const BorderSide(
                                color: AppTheme.primaryColor, width: 2)
                            : BorderSide.none,
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: _tierColor(tier),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Text(
                                    plan['name'] ?? '',
                                    style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold),
                                  ),
                                ),
                                const Spacer(),
                                Text(
                                  plan['price'] == 0
                                      ? 'FREE'
                                      : '\u20B9${plan['price']}',
                                  style: Theme.of(context)
                                      .textTheme
                                      .headlineSmall
                                      ?.copyWith(fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(plan['description'] ?? '',
                                style: const TextStyle(color: Colors.grey)),
                            const SizedBox(height: 12),
                            _FeatureRow('Interests/day',
                                '${plan['max_interests_per_day']}'),
                            _FeatureRow('Messages/day',
                                '${plan['max_messages_per_day']}'),
                            _FeatureRow(
                                'View contact', plan['can_see_contact'] == true ? 'Yes' : 'No'),
                            _FeatureRow(
                                'View horoscope', plan['can_see_horoscope'] == true ? 'Yes' : 'No'),
                            _FeatureRow('Chat', plan['can_chat'] == true ? 'Yes' : 'No'),
                            _FeatureRow(
                                'AI Matches', plan['ai_match_recommendations'] == true ? 'Yes' : 'No'),
                            _FeatureRow(
                                'Profile Boost', plan['profile_boost'] == true ? 'Yes' : 'No'),
                            const SizedBox(height: 12),
                            SizedBox(
                              width: double.infinity,
                              child: isCurrent
                                  ? const OutlinedButton(
                                      onPressed: null,
                                      child: Text('Current Plan'),
                                    )
                                  : ElevatedButton(
                                      onPressed: () =>
                                          _subscribe(plan['id'].toString()),
                                      child: const Text('Subscribe'),
                                    ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
    );
  }
}

class _FeatureRow extends StatelessWidget {
  final String feature;
  final String value;
  const _FeatureRow(this.feature, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(
            value == 'Yes' ? Icons.check_circle : Icons.remove_circle_outline,
            size: 16,
            color: value == 'Yes' ? Colors.green : Colors.grey,
          ),
          const SizedBox(width: 8),
          Expanded(child: Text(feature, style: const TextStyle(fontSize: 13))),
          Text(value,
              style:
                  const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}
