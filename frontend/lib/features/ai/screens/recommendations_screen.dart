import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _daily = [];
  List<dynamic> _weekly = [];
  List<dynamic> _similar = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadAll();
  }

  Future<void> _loadAll() async {
    try {
      final dailyRes = await ApiService().getDailyRecommendations();
      final weeklyRes = await ApiService().getWeeklyRecommendations();
      final similarRes = await ApiService().getSimilarProfiles();
      if (mounted) {
        setState(() {
          _daily = dailyRes.data['recommendations'] ?? [];
          _weekly = weeklyRes.data['recommendations'] ?? [];
          _similar = similarRes.data['recommendations'] ?? [];
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Widget _buildList(List<dynamic> items) {
    if (items.isEmpty) {
      return const Center(
        child: Text('No recommendations available.\nComplete your profile for better matches!'),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: InkWell(
            onTap: () => context.push('/profile/${item['user_id']}'),
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                    child: const Icon(Icons.person, color: AppTheme.primaryColor),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item['display_name'] ?? 'Profile',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        if (item['match_reason'] != null)
                          Text(
                            item['match_reason'],
                            style: const TextStyle(
                                fontSize: 12, color: Colors.grey),
                            maxLines: 2,
                          ),
                      ],
                    ),
                  ),
                  Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryColor,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          '${item['compatibility_score'] ?? 0}%',
                          style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14),
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text('Match',
                          style: TextStyle(fontSize: 10, color: Colors.grey)),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Recommendations'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'Daily (${_daily.length})'),
            Tab(text: 'Weekly (${_weekly.length})'),
            Tab(text: 'Similar (${_similar.length})'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildList(_daily),
                _buildList(_weekly),
                _buildList(_similar),
              ],
            ),
    );
  }
}
