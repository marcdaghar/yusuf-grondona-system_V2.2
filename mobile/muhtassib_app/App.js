/**
 * Muhtassib App – Application mobile pour les inspecteurs du marché
 * ==================================================================
 *
 * Application React Native pour les muhtassib :
 * - Inspections terrain
 * - Gestion de la réputation
 * - Alertes en temps réel
 * - Scan de QR codes (certificats halal)
 * - Prise de preuves photo
 *
 * Installation:
 *     npx react-native init MuhtassibApp
 *     cd MuhtassibApp
 *     npm install @react-native-async-storage/async-storage react-native-qrcode-scanner
 *
 * License: CC BY-SA 4.0 – Marc Daghar
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  RefreshControl,
  FlatList,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useNavigation } from '@react-navigation/native';

// ---- Configuration ----
const API_URL = 'https://api.yusuf-grondona.com';

// ---- Composant principal ----
export default function App() {
  const navigation = useNavigation();

  // ---- State ----
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('muhtassib_ahmed');
  const [password, setPassword] = useState('inspect123');
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // ---- Données ----
  const [inspections, setInspections] = useState([]);
  const [pendingAlerts, setPendingAlerts] = useState([]);
  const [reputation, setReputation] = useState(0);
  const [tasks, setTasks] = useState([]);

  // ---- Formulaire d'inspection ----
  const [currentInspection, setCurrentInspection] = useState({
    merchant: '',
    merchant_id: '',
    weight_kg: '',
    halal_certified: false,
    halal_valid: false,
    price: '',
    product: '',
    notes: '',
    latitude: null,
    longitude: null,
  });

  // ---- Effets ----
  useEffect(() => {
    loadStoredData();
  }, []);

  useEffect(() => {
    if (token) {
      fetchInspections();
      fetchTasks();
      fetchReputation();
      fetchAlerts();
    }
  }, [token]);

  // ---- Fonctions de stockage ----
  const loadStoredData = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      const storedReputation = await AsyncStorage.getItem('reputation');

      if (storedToken) {
        setToken(storedToken);
        setIsAuthenticated(true);
      }

      if (storedReputation) {
        setReputation(parseInt(storedReputation));
      }
    } catch (error) {
      console.error('Erreur de chargement:', error);
    }
  };

  const storeToken = async (newToken) => {
    try {
      await AsyncStorage.setItem('token', newToken);
      setToken(newToken);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Erreur de stockage:', error);
    }
  };

  const storeReputation = async (newReputation) => {
    try {
      await AsyncStorage.setItem('reputation', newReputation.toString());
      setReputation(newReputation);
    } catch (error) {
      console.error('Erreur de stockage:', error);
    }
  };

  // ---- Authentification ----
  const login = async () => {
    if (!username || !password) {
      Alert.alert('Erreur', 'Veuillez entrer vos identifiants');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        await storeToken(data.access_token);
        Alert.alert('Succès', 'Connecté en tant que muhtassib');
        // Navigation vers le tableau de bord
      } else {
        Alert.alert('Erreur', data.detail || 'Identifiants incorrects');
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de se connecter');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await AsyncStorage.removeItem('token');
      setToken(null);
      setIsAuthenticated(false);
      setInspections([]);
      setTasks([]);
      setPendingAlerts([]);
    } catch (error) {
      console.error('Erreur de déconnexion:', error);
    }
  };

  // ---- API Calls ----
  const fetchInspections = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/mobile/history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setInspections(data.inspections || []);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchTasks = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/mobile/tasks`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setTasks(data || []);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchReputation = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/mobile/reputation/muhtassib_ahmed`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setReputation(data.reputation || 0);
      }
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const fetchAlerts = async () => {
    // Simulation d'alertes
    setPendingAlerts([
      { id: 1, message: 'Inspection programmée: Boulangerie des Oliviers', priority: 'high' },
      { id: 2, message: 'Certificat halal à vérifier: Épicerie Al-Nour', priority: 'medium' },
    ]);
  };

  // ---- Soumettre une inspection ----
  const submitInspection = async () => {
    if (!currentInspection.merchant || !currentInspection.weight_kg) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/mobile/inspect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          muhtassib_id: username,
          merchant: currentInspection.merchant,
          merchant_id: currentInspection.merchant_id || `merchant_${Date.now()}`,
          weight_kg: parseFloat(currentInspection.weight_kg),
          halal_certified: currentInspection.halal_certified,
          halal_valid: currentInspection.halal_valid,
          price: currentInspection.price ? parseFloat(currentInspection.price) : null,
          product: currentInspection.product,
          notes: currentInspection.notes,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert(
          'Inspection enregistrée',
          `Conformité: ${data.compliant ? '✅ Conforme' : '❌ Non conforme'}\nRéputation: ${data.reputation_change > 0 ? '+' : ''}${data.reputation_change} points`
        );

        // Mise à jour de la réputation
        if (data.reputation_change) {
          const newRep = reputation + data.reputation_change;
          await storeReputation(newRep);
        }

        // Réinitialisation du formulaire
        setCurrentInspection({
          merchant: '',
          merchant_id: '',
          weight_kg: '',
          halal_certified: false,
          halal_valid: false,
          price: '',
          product: '',
          notes: '',
          latitude: null,
          longitude: null,
        });

        // Rafraîchissement des données
        fetchInspections();
        fetchTasks();
      } else {
        Alert.alert('Erreur', data.detail || 'Échec de l\'enregistrement');
      }
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de soumettre l\'inspection');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // ---- Rafraîchissement ----
  const onRefresh = async () => {
    setRefreshing(true);
    await fetchInspections();
    await fetchTasks();
    await fetchReputation();
    await fetchAlerts();
    setRefreshing(false);
  };

  // ---- Rendu ----
  if (!isAuthenticated) {
    return (
      <ScrollView style={styles.container} contentContainerStyle={styles.centerContent}>
        <View style={styles.loginContainer}>
          <Text style={styles.title}>🕌 Muhtassib</Text>
          <Text style={styles.subtitle}>Inspecteur du marché</Text>

          <TextInput
            style={styles.input}
            placeholder="Nom d'utilisateur"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
          />

          <TextInput
            style={styles.input}
            placeholder="Mot de passe"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <TouchableOpacity
            style={styles.loginButton}
            onPress={login}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.loginButtonText}>Se connecter</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.version}>Yusuf-Grondona v1.0.0</Text>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* En-tête */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Muhtassib</Text>
          <Text style={styles.headerSubtitle}>{username}</Text>
        </View>
        <View style={styles.reputationBox}>
          <Text style={styles.reputationLabel}>⭐ Réputation</Text>
          <Text style={styles.reputationValue}>{reputation}</Text>
        </View>
      </View>

      {/* Alertes */}
      {pendingAlerts.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🚨 Alertes</Text>
          {pendingAlerts.map((alert) => (
            <View
              key={alert.id}
              style={[
                styles.alertCard,
                alert.priority === 'high' && styles.alertHigh,
                alert.priority === 'medium' && styles.alertMedium,
              ]}
            >
              <Text style={styles.alertText}>{alert.message}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Tâches */}
      {tasks.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📋 Inspections à réaliser</Text>
          {tasks.map((task) => (
            <View key={task.id} style={styles.taskCard}>
              <Text style={styles.taskMerchant}>{task.merchant}</Text>
              <Text style={styles.taskDetail}>📅 {task.scheduled_date}</Text>
              <Text style={styles.taskDetail}>📍 {task.address}</Text>
              <Text style={styles.taskPriority}>🔴 {task.priority}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Formulaire d'inspection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔍 Nouvelle inspection</Text>

        <TextInput
          style={styles.input}
          placeholder="Nom du commerçant *"
          value={currentInspection.merchant}
          onChangeText={(text) => setCurrentInspection({ ...currentInspection, merchant: text })}
        />

        <TextInput
          style={styles.input}
          placeholder="ID du commerçant"
          value={currentInspection.merchant_id}
          onChangeText={(text) => setCurrentInspection({ ...currentInspection, merchant_id: text })}
        />

        <TextInput
          style={styles.input}
          placeholder="Poids (kg) *"
          keyboardType="numeric"
          value={currentInspection.weight_kg}
          onChangeText={(text) => setCurrentInspection({ ...currentInspection, weight_kg: text })}
        />

        <TextInput
          style={styles.input}
          placeholder="Produit"
          value={currentInspection.product}
          onChangeText={(text) => setCurrentInspection({ ...currentInspection, product: text })}
        />

        <TextInput
          style={styles.input}
          placeholder="Prix (fulus)"
          keyboardType="numeric"
          value={currentInspection.price}
          onChangeText={(text) => setCurrentInspection({ ...currentInspection, price: text })}
        />

        <View style={styles.checkboxContainer}>
          <TouchableOpacity
            style={[
              styles.checkbox,
              currentInspection.halal_certified && styles.checkboxChecked,
            ]}
            onPress={() => setCurrentInspection({
              ...currentInspection,
              halal_certified: !currentInspection.halal_certified,
            })}
          >
            <Text style={styles.checkboxText}>
              {currentInspection.halal_certified ? '✅' : '⬜'} Certificat halal présent
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.checkbox,
              currentInspection.halal_valid && styles.checkboxChecked,
            ]}
            onPress={() => setCurrentInspection({
              ...currentInspection,
              halal_valid: !currentInspection.halal_valid,
            })}
            disabled={!currentInspection.halal_certified}
          >
            <Text style={styles.checkboxText}>
              {currentInspection.halal_valid ? '✅' : '⬜'} Certificat valide
            </Text>
          </TouchableOpacity>
        </View>

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Notes"
          multiline
          numberOfLines={3}
          value={currentInspection.notes}
          onChangeText={(text) => setCurrentInspection({ ...currentInspection, notes: text })}
        />

        <TouchableOpacity
          style={styles.submitButton}
          onPress={submitInspection}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>📤 Soumettre l'inspection</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Historique */}
      {inspections.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📋 Inspections récentes</Text>
          {inspections.slice(0, 5).map((insp, idx) => (
            <View key={idx} style={styles.inspectionCard}>
              <View style={styles.inspectionHeader}>
                <Text style={styles.inspectionMerchant}>{insp.merchant}</Text>
                <Text style={insp.compliant ? styles.compliant : styles.nonCompliant}>
                  {insp.compliant ? '✅' : '❌'}
                </Text>
              </View>
              <Text style={styles.inspectionDetail}>⚖️ {insp.weight_kg} kg</Text>
              {insp.product && (
                <Text style={styles.inspectionDetail}>📦 {insp.product}</Text>
              )}
              <Text style={styles.inspectionDate}>
                {new Date(insp.timestamp * 1000).toLocaleDateString()}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* Déconnexion */}
      <TouchableOpacity style={styles.logoutButton} onPress={logout}>
        <Text style={styles.logoutButtonText}>🚪 Se déconnecter</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>Yusuf-Grondona System v1.0.0 – CC BY-SA 4.0</Text>
    </ScrollView>
  );
}

// ---- Styles ----
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  centerContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginContainer: {
    width: '100%',
    maxWidth: 400,
    padding: 24,
    backgroundColor: '#fff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2E8B57',
    textAlign: 'center',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 24,
  },
  input: {
    backgroundColor: '#f8f9fa',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 16,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  loginButton: {
    backgroundColor: '#2E8B57',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
  },
  loginButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  version: {
    textAlign: 'center',
    color: '#999',
    fontSize: 12,
    marginTop: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2E8B57',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  reputationBox: {
    backgroundColor: '#f8f9fa',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  reputationLabel: {
    fontSize: 12,
    color: '#666',
  },
  reputationValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFD700',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  alertCard: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    backgroundColor: '#fff3cd',
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  alertHigh: {
    backgroundColor: '#f8d7da',
    borderLeftColor: '#dc3545',
  },
  alertMedium: {
    backgroundColor: '#fff3cd',
    borderLeftColor: '#ffc107',
  },
  alertText: {
    fontSize: 14,
    color: '#333',
  },
  taskCard: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  taskMerchant: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  taskDetail: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  taskPriority: {
    fontSize: 12,
    color: '#dc3545',
    marginTop: 4,
  },
  checkboxContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  checkbox: {
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  checkboxChecked: {
    backgroundColor: '#d4edda',
    borderColor: '#2E8B57',
  },
  checkboxText: {
    fontSize: 14,
    color: '#333',
  },
  submitButton: {
    backgroundColor: '#2E8B57',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  inspectionCard: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#eee',
  },
  inspectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  inspectionMerchant: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  inspectionDetail: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  inspectionDate: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  compliant: {
    fontSize: 18,
    color: '#2E8B57',
  },
  nonCompliant: {
    fontSize: 18,
    color: '#dc3545',
  },
  logoutButton: {
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderWidth: 1,
    borderColor: '#ddd',
    marginBottom: 8,
  },
  logoutButtonText: {
    fontSize: 16,
    color: '#dc3545',
  },
  footer: {
    textAlign: 'center',
    color: '#999',
    fontSize: 12,
    marginVertical: 16,
  },
});
