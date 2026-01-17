import React, { useState } from 'react';
import { User, Trash2, Save, ArrowLeft, AlertTriangle } from 'lucide-react';
import api from '../services/api';
import { SOIL_TYPE_OPTIONS } from '../utils/constants';

const ProfileScreen = ({ user, onBack, onLogout, onUpdateUser, onNavigate }) => {
    const [formData, setFormData] = useState({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone_number: user.phone || '',
        governorate: user.governorate || '',
        farm_type: user.farm_type || 'rain_fed',
        soil_type: user.soil_type || 'UNKNOWN',
        farm_size_ha: user.farm_size || ''
    });

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [error, setError] = useState(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    const governorates = [
        'Tunis', 'Ariana', 'Ben Arous', 'Manouba', 'Nabeul', 'Zaghouan',
        'Bizerte', 'Beja', 'Jendouba', 'Kef', 'Siliana', 'Kairouan',
        'Kasserine', 'Sidi Bouzid', 'Sousse', 'Monastir', 'Mahdia',
        'Sfax', 'Gafsa', 'Tozeur', 'Kebili', 'Gabes', 'Medenine', 'Tataouine'
    ];

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);
        setError(null);
        try {
            const response = await api.updateProfile(formData);
            setMessage('Profile updated successfully');
            if (response.user && onUpdateUser) {
                onUpdateUser(response.user);
            }
        } catch (err) {
            setError(err.message || 'Failed to update profile');
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (!showDeleteConfirm) {
            setShowDeleteConfirm(true);
            return;
        }

        setLoading(true);
        try {
            await api.deleteAccount();
            onLogout(); // Log user out and redirect to auth
        } catch (err) {
            setError(err.message);
            setLoading(false);
            setShowDeleteConfirm(false);
        }
    };

    return (
        <div className="w-full max-w-[1600px] mx-auto p-4 sm:p-6 lg:p-12 space-y-12 pb-20">
            <div className="flex items-center gap-4">
                <button
                    onClick={onBack}
                    className="p-2 hover:bg-slate-100 rounded-full transition-colors"
                >
                    <ArrowLeft className="text-slate-600" size={24} />
                </button>
                <h1 className="text-2xl font-bold text-slate-900">Account Settings</h1>
            </div>

            {message && (
                <div className="bg-emerald-50 text-emerald-700 p-4 rounded-xl flex items-center gap-3">
                    <div className="bg-emerald-100 p-1 rounded-full"><User size={16} /></div>
                    {message}
                </div>
            )}

            {error && (
                <div className="bg-red-50 text-red-700 p-4 rounded-xl flex items-center gap-3">
                    <AlertTriangle size={20} />
                    {error}
                </div>
            )}

            {/* Profile Form */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className="bg-blue-100 p-2 rounded-lg text-blue-600">
                        <User size={24} />
                    </div>
                    <h2 className="text-lg font-bold text-slate-800">Personal Information</h2>
                </div>

                <form onSubmit={handleUpdateProfile} className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                            <input
                                type="text"
                                value={formData.first_name}
                                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                className="w-full p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                            <input
                                type="text"
                                value={formData.last_name}
                                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                className="w-full p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number</label>
                        <input
                            type="tel"
                            value={formData.phone_number}
                            disabled
                            className="w-full p-3 rounded-lg border border-slate-200 bg-slate-50 text-slate-500 cursor-not-allowed"
                        />
                        <p className="text-xs text-slate-400 mt-1">Phone number cannot be changed</p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Governorate</label>
                            <select
                                value={formData.governorate}
                                onChange={(e) => setFormData({ ...formData, governorate: e.target.value })}
                                className="w-full p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
                            >
                                {governorates.map(gov => (
                                    <option key={gov} value={gov}>{gov}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Farm Type</label>
                            <select
                                value={formData.farm_type}
                                onChange={(e) => setFormData({ ...formData, farm_type: e.target.value })}
                                className="w-full p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
                            >
                                <option value="rain_fed">Rain Fed</option>
                                <option value="irrigated">Irrigated</option>
                                <option value="greenhouse">Greenhouse</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Soil Type</label>
                            <select
                                value={formData.soil_type}
                                onChange={(e) => setFormData({ ...formData, soil_type: e.target.value })}
                                className="w-full p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white"
                            >
                                {SOIL_TYPE_OPTIONS.map(option => (
                                    <option key={option.value} value={option.value}>
                                        {option.emoji} {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Farm Size (hectares)</label>
                            <input
                                type="number"
                                step="0.1"
                                min="0"
                                value={formData.farm_size_ha}
                                onChange={(e) => setFormData({ ...formData, farm_size_ha: e.target.value })}
                                placeholder="e.g., 2.5"
                                className="w-full p-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                        </div>
                    </div>

                    <div className="pt-4 flex justify-end">
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center gap-2 bg-emerald-600 text-white px-6 py-2.5 rounded-xl font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        >
                            <Save size={18} />
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>





            {/* Danger Zone */}
            <div className="bg-red-50 rounded-2xl border border-red-100 p-6">
                <div className="flex items-center gap-3 mb-4">
                    <Trash2 className="text-red-600" size={24} />
                    <h2 className="text-lg font-bold text-red-900">Danger Zone</h2>
                </div>

                <p className="text-red-800 mb-6 text-sm">
                    Deleting your account is permanent. All your data, including decision history and analytics, will be wiped immediately.
                </p>

                <div className="flex justify-end">
                    {showDeleteConfirm ? (
                        <div className="flex items-center gap-3 bg-white p-2 rounded-lg shadow-sm border border-red-100">
                            <span className="text-sm font-medium text-red-700 px-2">Are you sure?</span>
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                className="px-3 py-1 text-sm text-slate-600 hover:text-slate-800"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleDeleteAccount}
                                className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                            >
                                Yes, Delete
                            </button>
                        </div>
                    ) : (
                        <button
                            onClick={() => setShowDeleteConfirm(true)}
                            className="px-4 py-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-100 text-sm font-medium transition-colors"
                        >
                            Delete Account
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ProfileScreen;
