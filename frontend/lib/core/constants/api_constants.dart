class ApiConstants {
  ApiConstants._();

  static const String baseUrl = 'http://localhost:8000';
  static const String apiPrefix = '/api/v1';

  // Auth
  static const String sendOtp = '$apiPrefix/auth/otp/send';
  static const String verifyOtp = '$apiPrefix/auth/otp/verify';
  static const String register = '$apiPrefix/auth/register';
  static const String loginEmail = '$apiPrefix/auth/login/email';
  static const String refreshToken = '$apiPrefix/auth/token/refresh';

  // Profiles
  static const String profiles = '$apiPrefix/profiles';
  static const String myProfile = '$apiPrefix/profiles/me';
  static const String searchProfiles = '$apiPrefix/profiles/search';

  // Horoscope
  static const String horoscope = '$apiPrefix/horoscope';
  static const String myHoroscope = '$apiPrefix/horoscope/me';
  static const String uploadHoroscopePdf = '$apiPrefix/horoscope/upload-pdf';

  // Photos
  static const String uploadPhoto = '$apiPrefix/photos/upload';
  static const String myPhotos = '$apiPrefix/photos/my-photos';
  static const String selfieVerify = '$apiPrefix/photos/selfie-verify';

  // Matches
  static const String sendInterest = '$apiPrefix/matches/send-interest';
  static const String sentInterests = '$apiPrefix/matches/sent';
  static const String receivedInterests = '$apiPrefix/matches/received';

  // Chat
  static const String chatRooms = '$apiPrefix/chat/rooms';
  static String chatWebSocket(String roomId) =>
      '$apiPrefix/chat/ws/$roomId';

  // Notifications
  static const String notifications = '$apiPrefix/notifications';

  // Subscriptions
  static const String plans = '$apiPrefix/subscriptions/plans';
  static const String mySubscription = '$apiPrefix/subscriptions/my-subscription';
  static const String subscribe = '$apiPrefix/subscriptions/subscribe';

  // AI
  static const String dailyRecommendations = '$apiPrefix/ai/recommendations/daily';
  static const String weeklyRecommendations = '$apiPrefix/ai/recommendations/weekly';
  static const String similarProfiles = '$apiPrefix/ai/recommendations/similar';
  static const String chatAssistant = '$apiPrefix/ai/chat-assistant';
  static const String profileSuggestions = '$apiPrefix/ai/profile-suggestions';

  // Admin
  static const String adminDashboard = '$apiPrefix/admin/dashboard';
  static const String adminPendingProfiles = '$apiPrefix/admin/profiles/pending';
  static const String adminFraudAlerts = '$apiPrefix/admin/fraud-alerts';
  static const String adminAuditLogs = '$apiPrefix/admin/audit-logs';
}
