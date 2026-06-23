import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../constants/api_constants.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  late final Dio _dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  ApiService._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: 'access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final opts = error.requestOptions;
            final token = await _storage.read(key: 'access_token');
            opts.headers['Authorization'] = 'Bearer $token';
            final response = await _dio.fetch(opts);
            return handler.resolve(response);
          }
        }
        return handler.next(error);
      },
    ));
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.read(key: 'refresh_token');
      if (refreshToken == null) return false;

      final response = await Dio().post(
        '${ApiConstants.baseUrl}${ApiConstants.refreshToken}',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        await _storage.write(
            key: 'access_token', value: response.data['access_token']);
        await _storage.write(
            key: 'refresh_token', value: response.data['refresh_token']);
        return true;
      }
    } catch (_) {}
    return false;
  }

  // Auth
  Future<Response> sendOtp(String phone) =>
      _dio.post(ApiConstants.sendOtp, data: {'phone': phone});

  Future<Response> verifyOtp(String phone, String otp) =>
      _dio.post(ApiConstants.verifyOtp, data: {'phone': phone, 'otp': otp});

  Future<Response> register(Map<String, dynamic> data) =>
      _dio.post(ApiConstants.register, data: data);

  Future<Response> loginEmail(String email, String password) =>
      _dio.post(ApiConstants.loginEmail,
          data: {'email': email, 'password': password});

  // Profile
  Future<Response> getMyProfile() => _dio.get(ApiConstants.myProfile);

  Future<Response> createProfile(Map<String, dynamic> data) =>
      _dio.post(ApiConstants.profiles, data: data);

  Future<Response> updateProfile(Map<String, dynamic> data) =>
      _dio.put(ApiConstants.myProfile, data: data);

  Future<Response> getProfile(String userId) =>
      _dio.get('${ApiConstants.profiles}/$userId');

  Future<Response> searchProfiles(Map<String, dynamic> filters) =>
      _dio.post(ApiConstants.searchProfiles, data: filters);

  // Photos
  Future<Response> uploadPhoto(String filePath, String photoType) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath),
      'photo_type': photoType,
    });
    return _dio.post(ApiConstants.uploadPhoto, data: formData);
  }

  Future<Response> getMyPhotos() => _dio.get(ApiConstants.myPhotos);

  Future<Response> deletePhoto(String photoId) =>
      _dio.delete('${ApiConstants.myPhotos.replaceAll('my-photos', photoId)}');

  Future<Response> selfieVerify(String filePath) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath),
    });
    return _dio.post(ApiConstants.selfieVerify, data: formData);
  }

  // Horoscope
  Future<Response> getMyHoroscope() => _dio.get(ApiConstants.myHoroscope);

  Future<Response> createHoroscope(Map<String, dynamic> data) =>
      _dio.post(ApiConstants.horoscope, data: data);

  Future<Response> updateHoroscope(Map<String, dynamic> data) =>
      _dio.put(ApiConstants.myHoroscope, data: data);

  // Matches
  Future<Response> sendInterest(String receiverId, {String? message}) =>
      _dio.post(ApiConstants.sendInterest,
          data: {'receiver_id': receiverId, 'message': message});

  Future<Response> respondInterest(String matchId, String action,
          {String? reason}) =>
      _dio.put('${ApiConstants.sentInterests.replaceAll('sent', matchId)}/respond',
          data: {'action': action, 'rejection_reason': reason});

  Future<Response> getSentInterests({int page = 1}) =>
      _dio.get(ApiConstants.sentInterests, queryParameters: {'page': page});

  Future<Response> getReceivedInterests({int page = 1}) =>
      _dio.get(ApiConstants.receivedInterests,
          queryParameters: {'page': page});

  // Chat
  Future<Response> getChatRooms() => _dio.get(ApiConstants.chatRooms);

  Future<Response> getChatMessages(String roomId, {int page = 1}) =>
      _dio.get('${ApiConstants.chatRooms}/$roomId/messages',
          queryParameters: {'page': page});

  Future<Response> sendMessage(String roomId, String content) =>
      _dio.post('${ApiConstants.chatRooms}/$roomId/messages',
          data: {'content': content});

  // Notifications
  Future<Response> getNotifications({bool unreadOnly = false}) =>
      _dio.get(ApiConstants.notifications,
          queryParameters: {'unread_only': unreadOnly});

  Future<Response> markNotificationRead(String id) =>
      _dio.put('${ApiConstants.notifications}/$id/read');

  Future<Response> markAllNotificationsRead() =>
      _dio.put('${ApiConstants.notifications}/read-all');

  // Subscriptions
  Future<Response> getPlans() => _dio.get(ApiConstants.plans);

  Future<Response> getMySubscription() =>
      _dio.get(ApiConstants.mySubscription);

  Future<Response> subscribePlan(String planId) =>
      _dio.post(ApiConstants.subscribe, data: {'plan_id': planId});

  // AI
  Future<Response> getDailyRecommendations() =>
      _dio.get(ApiConstants.dailyRecommendations);

  Future<Response> getWeeklyRecommendations() =>
      _dio.get(ApiConstants.weeklyRecommendations);

  Future<Response> getSimilarProfiles() =>
      _dio.get(ApiConstants.similarProfiles);

  Future<Response> chatWithAssistant(String query, {String? context}) =>
      _dio.post(ApiConstants.chatAssistant,
          data: {'query': query, 'context': context});

  Future<Response> getProfileSuggestions() =>
      _dio.get(ApiConstants.profileSuggestions);

  // Token management
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<bool> hasToken() async {
    final token = await _storage.read(key: 'access_token');
    return token != null;
  }
}
