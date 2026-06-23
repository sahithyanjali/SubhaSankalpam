import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class MatchesScreen extends StatefulWidget {
  const MatchesScreen({super.key});

  @override
  State<MatchesScreen> createState() => _MatchesScreenState();
}

class _MatchesScreenState extends State<MatchesScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _sent = [];
  List<dynamic> _received = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadMatches();
  }

  Future<void> _loadMatches() async {
    try {
      final sentRes = await ApiService().getSentInterests();
      final receivedRes = await ApiService().getReceivedInterests();
      if (mounted) {
        setState(() {
          _sent = sentRes.data['matches'] ?? [];
          _received = receivedRes.data['matches'] ?? [];
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _respondInterest(String matchId, String action) async {
    try {
      await ApiService().respondInterest(matchId, action);
      _loadMatches();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content:
                  Text('Interest ${action == "accept" ? "accepted" : "rejected"}')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
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
        title: const Text('My Matches'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: 'Received (${_received.length})'),
            Tab(text: 'Sent (${_sent.length})'),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                // Received
                _received.isEmpty
                    ? const Center(child: Text('No interests received yet'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _received.length,
                        itemBuilder: (context, index) {
                          final match = _received[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      CircleAvatar(
                                        backgroundColor: AppTheme.primaryColor
                                            .withOpacity(0.1),
                                        child: const Icon(Icons.person,
                                            color: AppTheme.primaryColor),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              match['sender_name'] ?? 'User',
                                              style: const TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 16),
                                            ),
                                            if (match['compatibility_score'] !=
                                                null)
                                              Text(
                                                'Compatibility: ${match['compatibility_score']}%',
                                                style: TextStyle(
                                                    color: AppTheme.primaryColor,
                                                    fontSize: 13),
                                              ),
                                          ],
                                        ),
                                      ),
                                      if (match['status'] == 'pending') ...[
                                        IconButton(
                                          icon: const Icon(Icons.check_circle,
                                              color: Colors.green),
                                          onPressed: () => _respondInterest(
                                              match['id'], 'accept'),
                                        ),
                                        IconButton(
                                          icon: const Icon(Icons.cancel,
                                              color: Colors.red),
                                          onPressed: () => _respondInterest(
                                              match['id'], 'reject'),
                                        ),
                                      ] else
                                        Chip(
                                          label: Text(
                                            match['status']
                                                    ?.toString()
                                                    .toUpperCase() ??
                                                '',
                                            style:
                                                const TextStyle(fontSize: 11),
                                          ),
                                        ),
                                    ],
                                  ),
                                  if (match['message'] != null) ...[
                                    const SizedBox(height: 8),
                                    Text(match['message'],
                                        style: const TextStyle(
                                            color: Colors.grey)),
                                  ],
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                // Sent
                _sent.isEmpty
                    ? const Center(child: Text('No interests sent yet'))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _sent.length,
                        itemBuilder: (context, index) {
                          final match = _sent[index];
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
                                  match['receiver_name'] ?? 'Profile'),
                              subtitle: Text(
                                  'Status: ${match['status'] ?? 'pending'}'),
                              trailing: match['status'] == 'accepted'
                                  ? IconButton(
                                      icon: const Icon(Icons.chat,
                                          color: AppTheme.primaryColor),
                                      onPressed: () => context.push(
                                          '/chat/${match['chat_room_id']}',
                                          extra: match['receiver_name']),
                                    )
                                  : null,
                              onTap: () => context
                                  .push('/profile/${match['receiver_id']}'),
                            ),
                          );
                        },
                      ),
              ],
            ),
    );
  }
}
