/**
 * Local storage service
 */
import { LOCAL_STORAGE_KEYS } from '../utils/constants';

class StorageService {
  /**
   * Save user data to localStorage
   */
  saveUser(user) {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEYS.USER, JSON.stringify(user));
    } catch (error) {
      console.error('Failed to save user:', error);
    }
  }

  /**
   * Get user data from localStorage
   */
  getUser() {
    try {
      const userData = localStorage.getItem(LOCAL_STORAGE_KEYS.USER);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Failed to get user:', error);
      return null;
    }
  }

  /**
   * Clear all user data
   */
  clearUser() {
    try {
      localStorage.removeItem(LOCAL_STORAGE_KEYS.USER);
      localStorage.removeItem(LOCAL_STORAGE_KEYS.TOKEN);
    } catch (error) {
      console.error('Failed to clear user data:', error);
    }
  }

  /**
   * Save generic data
   */
  saveData(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Failed to save data for key ${key}:`, error);
    }
  }

  /**
   * Get generic data
   */
  getData(key) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error(`Failed to get data for key ${key}:`, error);
      return null;
    }
  }

  /**
   * Remove generic data
   */
  removeData(key) {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove data for key ${key}:`, error);
    }
  }
}

export default new StorageService();