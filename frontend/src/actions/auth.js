import api from '../components/api/google_client'; // Ensure the correct path to the api instance

// Action Types
const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
const FETCH_USER_SUCCESS = 'FETCH_USER_SUCCESS';
const LOGOUT = 'LOGOUT';

// Action Creators
export const loginSuccess = (authToken) => ({
  type: LOGIN_SUCCESS,
  payload: authToken,
});

export const fetchUserSuccess = (user) => ({
  type: FETCH_USER_SUCCESS,
  payload: user,
});

export const logout = () => ({
  type: LOGOUT,
});

// Async Actions
export const fetchUser = (authToken) => async (dispatch) => {
  try {
    const response = await api.get('/api/user/', {
      headers: { Authorization: `Token ${authToken}` }
    });
    if (response.status === 200) {
      dispatch(fetchUserSuccess(response.data));
    }
  } catch (error) {
    console.error('Error fetching user:', error);
  }
};
