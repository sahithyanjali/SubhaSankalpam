import 'package:flutter/material.dart';

import '../../../core/services/api_service.dart';
import '../../../core/theme/app_theme.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<dynamic> _notifications = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadNotifications();
  }

  Future<void> _loadNotifications() async {
    try {
      final response = await ApiService().getNotifications();
      if (mounted) {
        setState(() {
          _notifications = response.data['notifications'] ?? [];
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _markAllRead() async {
    try {
      await ApiService().markAllNotificationsRead();
      _loadNotifications();
    } catch (_) {}
  }

  IconData _getIcon(String? type) {
    switch (type) {
      case 'interest_received':
        return Icons.favorite;
      case 'interest_accepted':
        return Icons.check_circle;
      case 'interest_rejected':
        return Icons.cancel;
      case 'new_message':
        return Icons.chat;
      case 'profile_viewed':
        return Icons.visibility;
      case 'match_suggestion':
        return Icons.auto_awesome;
      case 'subscription_expiry':
        return Icons.card_membership;
      default:
        return Icons.notifications;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          TextButton(
            onPressed: _markAllRead,
            child: const Text('Mark all read'),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _notifications.isEmpty
              ? const Center(child: Text('No notifications'))
              : RefreshIndicator(
                  onRefresh: _loadNotifications,
                  child: ListView.builder(
                    itemCount: _notifications.length,
                    itemBuilder: (context, index) {
                      final notif = _notifications[index];
                      final isRead = notif['is_read'] == true;
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: isRead
                              ? Colors.grey.shade200
                              : AppTheme.primaryColor.withOpacity(0.1),
                          child: Icon(
                            _getIcon(notif['notification_type']),
                            color: isRead
                                ? Colors.grey
                                : AppTheme.primaryColor,
                            size: 20,
                          ),
                        ),
                        title: Text(
                          notif['title'] ?? '',
                          style: TextStyle(
                            fontWeight:
                                isRead ? FontWeight.normal : FontWeight.bold,
                          ),
                        ),
                        subtitle: Text(notif['body'] ?? ''),
                        trailing: !isRead
                            ? Container(
                                width: 8,
                                height: 8,
                                decoration: const BoxDecoration(
                                  color: AppTheme.primaryColor,
                                  shape: BoxShape.circle,
                                ),
                              )
                            : null,
                        onTap: () async {
                          if (!isRead) {
                            await ApiService()
                                .markNotificationRead(notif['id']);
                            _loadNotifications();
                          }
                        },
                      );
                    },
                  ),
                ),
    );
  }
}
