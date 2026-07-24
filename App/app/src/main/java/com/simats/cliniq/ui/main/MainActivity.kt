package com.simats.cliniq.ui.main

import android.content.Intent
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.simats.cliniq.R
import com.simats.cliniq.data.local.SessionManager
import com.simats.cliniq.data.repository.AuthRepository
import com.simats.cliniq.databinding.ActivityMainBinding
import com.simats.cliniq.ui.auth.LoginActivity
import com.simats.cliniq.ui.doctor.*
import com.simats.cliniq.ui.lab.*
import com.simats.cliniq.ui.patient.*

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sessionManager = SessionManager.getInstance(this)

        if (!sessionManager.isLoggedIn()) {
            navigateToLogin()
            return
        }

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.toolbar)

        setupNavigationForRole()
    }

    private fun setupNavigationForRole() {
        val role = sessionManager.getUserRole()
        val user = sessionManager.getUser()

        supportActionBar?.title = when (role) {
            "PATIENT" -> "Patient Dashboard"
            "DOCTOR" -> "Doctor Dashboard"
            "LAB" -> "Lab Dashboard"
            else -> "ClinIQ"
        }
        supportActionBar?.subtitle = user?.fullName ?: user?.username

        val bottomNav = binding.bottomNavigation
        bottomNav.menu.clear()

        when (role) {
            "PATIENT" -> setupPatientNav(bottomNav)
            "DOCTOR" -> setupDoctorNav(bottomNav)
            "LAB" -> setupLabNav(bottomNav)
            else -> navigateToLogin()
        }
    }

    private fun setupPatientNav(bottomNav: BottomNavigationView) {
        bottomNav.inflateMenu(R.menu.menu_patient_bottom)
        loadFragment(PatientDashboardFragment())

        bottomNav.setOnItemSelectedListener { item ->
            val fragment: Fragment = when (item.itemId) {
                R.id.nav_patient_home -> PatientDashboardFragment()
                R.id.nav_patient_appointments -> PatientAppointmentsFragment()
                R.id.nav_patient_reports -> PatientReportsFragment()
                R.id.nav_patient_queries -> PatientQueriesFragment()
                R.id.nav_patient_profile -> PatientProfileFragment()
                else -> PatientDashboardFragment()
            }
            supportActionBar?.title = when (item.itemId) {
                R.id.nav_patient_home -> "Dashboard"
                R.id.nav_patient_appointments -> "Appointments"
                R.id.nav_patient_reports -> "Lab Reports"
                R.id.nav_patient_queries -> "Queries"
                R.id.nav_patient_profile -> "Profile"
                else -> "Dashboard"
            }
            loadFragment(fragment)
            true
        }
    }

    private fun setupDoctorNav(bottomNav: BottomNavigationView) {
        bottomNav.inflateMenu(R.menu.menu_doctor_bottom)
        loadFragment(DoctorDashboardFragment())

        bottomNav.setOnItemSelectedListener { item ->
            val fragment: Fragment = when (item.itemId) {
                R.id.nav_doctor_home -> DoctorDashboardFragment()
                R.id.nav_doctor_appointments -> DoctorAppointmentsFragment()
                R.id.nav_doctor_patients -> DoctorPatientsFragment()
                R.id.nav_doctor_queries -> DoctorQueriesFragment()
                R.id.nav_doctor_profile -> DoctorProfileFragment()
                else -> DoctorDashboardFragment()
            }
            supportActionBar?.title = when (item.itemId) {
                R.id.nav_doctor_home -> "Dashboard"
                R.id.nav_doctor_appointments -> "Appointments"
                R.id.nav_doctor_patients -> "My Patients"
                R.id.nav_doctor_queries -> "Queries"
                R.id.nav_doctor_profile -> "Profile"
                else -> "Dashboard"
            }
            loadFragment(fragment)
            true
        }
    }

    private fun setupLabNav(bottomNav: BottomNavigationView) {
        bottomNav.inflateMenu(R.menu.menu_lab_bottom)
        loadFragment(LabDashboardFragment())

        bottomNav.setOnItemSelectedListener { item ->
            val fragment: Fragment = when (item.itemId) {
                R.id.nav_lab_home -> LabDashboardFragment()
                R.id.nav_lab_appointments -> LabAppointmentsFragment()
                R.id.nav_lab_reports -> LabReportsFragment()
                R.id.nav_lab_profile -> LabProfileFragment()
                else -> LabDashboardFragment()
            }
            supportActionBar?.title = when (item.itemId) {
                R.id.nav_lab_home -> "Dashboard"
                R.id.nav_lab_appointments -> "Appointments"
                R.id.nav_lab_reports -> "Reports"
                R.id.nav_lab_profile -> "Profile"
                else -> "Dashboard"
            }
            loadFragment(fragment)
            true
        }
    }

    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commit()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        return when (item.itemId) {
            R.id.action_logout -> {
                logout()
                true
            }
            else -> super.onOptionsItemSelected(item)
        }
    }

    private fun logout() {
        AuthRepository(this).logout()
        Toast.makeText(this, "Logged out successfully", Toast.LENGTH_SHORT).show()
        navigateToLogin()
    }

    private fun navigateToLogin() {
        startActivity(Intent(this, LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        })
        finish()
    }
}
