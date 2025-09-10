export const ROUTES_API = {
  /// User - API - Routes

  customerOverview: "/api/user/overview",
  /// Business - Affiliate Customers - API - Routes
};

export const ROUTES_API_2 = {
  USER: {
    /// Retrieve user preferences
    preferences: (userId: string) => `/api/user/${userId}/preferences`,
    /// Retrieve user rewards
    rewards: (userId: string) => `/api/user/${userId}/rewards`,

    getUserByEmail: "/api/user/",

    searchUser: "/api/user/search",

    updateLastLogin: "/api/user/update-last-login",

    canLogin: "/api/user/get-can-login",

    /// Reservations - API
    getAllReservationByUserId: (userId: string) =>
      `/api/user/${userId}/reservations`,

    createReservationByUserId: (userId: string) =>
      `/api/user/${userId}/reservations`,

    deleteReservationByUserId: (userId: string, reservationId) =>
      `/api/user/${userId}/reservations/${reservationId}`,
  },

  CUSTOMER: {
    /// Overview (alias of userOverview)
    overview: "/api/user/overview",

    /// Get all Slot Configuration By BusinessActivity ID
    getBusinessOverviewSlotConfigByActivityId: (businessActivityId: string) =>
      `/api/user/overview/${businessActivityId}/slots`,

    /// CUSTOMER - REQUESTS - Management
    /// Get all Request
    getCustomerRequestById: (userId: string) =>
      `/api/customer/${userId}/requests`,
    /// Respond to BusinessActivity Request
    customerRequestsRespond: (customerId: string) =>
      `/api/customer/${customerId}/requests/respond`,

    /// CUSTOMER - FEEDBACKS - Management
    getCustomerFeedBackById: (userId: string) =>
      `/api/customer/${userId}/feedback`,
  },

  BUSINESS: {
    /// Create Slot Configuration for the reservations
    createBusinessSlotConfig: (
      businessOwnerId: string,
      businessActivityId: string,
    ) =>
      `/api/business/${businessOwnerId}/activities/${businessActivityId}/slots`,

    /// Get all Slot Configuration
    getBusinessSlotConfigByActivityId: (
      businessOwnerId: string,
      businessActivityId: string,
    ) =>
      `/api/business/${businessOwnerId}/activities/${businessActivityId}/slots`,

    /// Get all BusinessActivity of a Single BusinessUser
    getAllInfoBusinessActivityByOwnerId: (ownerBusinessId: string) =>
      `/api/business/${ownerBusinessId}/activities`,

    /// Get Single BusinessActivity of a Single BusinessUser
    getInfoBusinessActivityById: (
      ownerBusinessId: string,
      businessActivityId: string,
    ) => `/api/business/${ownerBusinessId}/activities/${businessActivityId}`,

    /// Create/update/delete activity info
    saveInfoBusinessActivity: (ownerBusinessId: string) =>
      `/api/business/${ownerBusinessId}/activities`,
    updateInfoBusinessActivity: (ownerBusinessId: string, businessActivityId) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}`,
    deleteInfoBusinessActivity: (ownerBusinessId: string, businessActivityId) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}`,

    /// BUSINESS - BusinessActivity - Reservations - Management
    getAllReservationsByBusinessActivityId: (
      ownerBusinessId: string,
      businessActivityId,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/reservations`,

    /// update Reservations BusinessActivity
    updateReservationByBusinessActivityId: (
      ownerBusinessId: string,
      businessActivityId: string,
      reservationId: string,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/reservations/${reservationId}`,
  },

  BUSINESS_AFFILIATES: {
    /// Get all affiliate customers
    getAllAffiliateCustomerBusinessActivity: (
      ownerBusinessId: string,
      businessActivityId: string,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/affiliates`,
    /// Send invitations to customers
    sendInvitations: (ownerBusinessId: string, businessActivityId: string) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/affiliates/invitations`,
    /// Delete an affiliate customer
    deleteAffiliateCustomerBusinessActivity: (
      ownerBusinessId: string,
      businessActivityId: string,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/affiliates/delete`,

    /// BUSINESS_STAFF - BusinessActivity - BusinessClient - FeedBack Management
    createFeedBackBusinessClient: (
      ownerBusinessId: string,
      businessActivityId: string,
      affiliateId: string,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/affiliates/${affiliateId}/feedback`,

    /// BUSINESS_STAFF - BusinessActivity - BusinessClient - FeedBack Management
    deleteFeedBackBusinessClient: (
      ownerBusinessId: string,
      businessActivityId: string,
      affiliateId: string,
      feedbackId: string,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/affiliates/${affiliateId}/feedback/${feedbackId}`,
  },

  BUSINESS_STAFF: {
    /// Get all staff for an activity
    getAll: (ownerBusinessId: string, businessActivityId: string) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/staff`,
    /// Add a staff member
    add: (ownerBusinessId: string, businessActivityId: string) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/staff`,
    /// Update a staff member
    update: (ownerBusinessId: string, businessActivityId: string) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/staff`,
    /// Delete a staff member
    delete: (ownerBusinessId: string, businessActivityId: string) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/staff`,
  },

  ADMIN: {
    /// Admin tag management

    getAllTags: "/api/admin/tags",

    createTag: "/api/admin/tags",

    deleteTags: (tagId: string) => `/api/admin/tags/${tagId}`,

    updateTags: (tagId: string) => `/api/admin/tags/${tagId}`,

    /// Admin Reward Management
    getAllRewards: "/api/admin/rewards",

    createReward: "/api/admin/rewards",

    deleteReward: (tagId: string) => `/api/admin/rewards/${tagId}`,

    updateReward: (tagId: string) => `/api/admin/rewards/${tagId}`,

    /// ADMIN - CUSTOMER - Management
    getAllCustomers: "/api/customer",

    updateCustomerLoginStatus: (customerId: string) =>
      `/api/customer/${customerId}`,

    /// udpateCustomerLoginStatus
    deleteCustomer: (customerId: string) => `/api/customer/${customerId}`,

    /// ADMIN - BusinessUser - Management
    getAllBusinessUser: "/api/business",

    /// Delete Business User
    deleteBusinessUser: (ownerBusinessId: string) =>
      `/api/business/${ownerBusinessId}`,

    /// ADMIN - BusinessActivity  - Management
    getAllBusinessActivityByBusinessId: (ownerBusinessId: string) =>
      `/api/business/${ownerBusinessId}/activities`,

    /// Create  BusinessActivity info
    saveInfoActivity: (ownerBusinessId: string) =>
      `/api/business/${ownerBusinessId}/activities`,
    /// Update BusinessActivity info
    updateInfoActivity: (ownerBusinessId: string, businessActivityId) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}`,

    deleteInfoActivity: (ownerBusinessId: string, businessActivityId) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}`,

    /// ADMIN - BusinessActivity  - Management
    getAllReservations: "/api/admin/reservations",
    /// Delete reservations by reservation ID
    deleteReservationById: (reservationId: string) =>
      `/api/admin/reservations/${reservationId}`,

    /// ADMIN - BusinessActivity - BusinessClient - FeedBack Management
    createFeedBackBusinessClient: (
      ownerBusinessId: string,
      businessActivityId: string,
      affiliateId: string,
    ) =>
      `/api/business/${ownerBusinessId}/activities/${businessActivityId}/affiliates/${affiliateId}/feedback`,
  },
};
