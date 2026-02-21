package com.nithin.healthapp.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.nithin.healthapp.R
import com.nithin.healthapp.databinding.ActivitySignupBinding

class SignupActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySignupBinding
    private val viewModel: AuthViewModel by viewModels()

    private val roles = listOf("PATIENT", "DOCTOR", "LAB")
    private val roleLabels = listOf("Patient", "Doctor", "Lab")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySignupBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUI()
        observeViewModel()
    }

    private fun setupUI() {
        // Setup role dropdown
        val adapter = ArrayAdapter(this, R.layout.item_dropdown, roleLabels)
        binding.actvRole.setAdapter(adapter)
        binding.actvRole.setText(roleLabels[0], false)

        binding.btnSignup.setOnClickListener {
            val email = binding.etEmail.text.toString().trim()
            val username = binding.etUsername.text.toString().trim()
            val password = binding.etPassword.text.toString().trim()
            val confirmPassword = binding.etConfirmPassword.text.toString().trim()
            val fullName = binding.etFullName.text.toString().trim().ifEmpty { null }
            val selectedRoleIndex = roleLabels.indexOf(binding.actvRole.text.toString())
            val role = if (selectedRoleIndex >= 0) roles[selectedRoleIndex] else "PATIENT"

            if (validateInput(email, username, password, confirmPassword)) {
                viewModel.signup(email, username, password, fullName, role)
            }
        }

        binding.tvLogin.setOnClickListener {
            finish()
        }

        binding.toolbar.setNavigationOnClickListener {
            finish()
        }
    }

    private fun validateInput(
        email: String, username: String,
        password: String, confirmPassword: String
    ): Boolean {
        var isValid = true

        if (email.isEmpty()) {
            binding.tilEmail.error = "Email is required"
            isValid = false
        } else if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            binding.tilEmail.error = "Invalid email"
            isValid = false
        } else {
            binding.tilEmail.error = null
        }

        if (username.isEmpty()) {
            binding.tilUsername.error = "Username is required"
            isValid = false
        } else if (username.length < 3) {
            binding.tilUsername.error = "Min 3 characters"
            isValid = false
        } else {
            binding.tilUsername.error = null
        }

        if (password.isEmpty()) {
            binding.tilPassword.error = "Password is required"
            isValid = false
        } else if (password.length < 8) {
            binding.tilPassword.error = "Min 8 characters"
            isValid = false
        } else {
            binding.tilPassword.error = null
        }

        if (confirmPassword != password) {
            binding.tilConfirmPassword.error = "Passwords don't match"
            isValid = false
        } else {
            binding.tilConfirmPassword.error = null
        }

        return isValid
    }

    private fun observeViewModel() {
        viewModel.isLoading.observe(this) { loading ->
            binding.progressBar.visibility = if (loading) View.VISIBLE else View.GONE
            binding.btnSignup.isEnabled = !loading
        }

        viewModel.signupResult.observe(this) { result ->
            result.onSuccess {
                Toast.makeText(this, "Account created! Please log in.", Toast.LENGTH_SHORT).show()
                startActivity(Intent(this, LoginActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
                })
                finish()
            }
            result.onFailure {
                Toast.makeText(this, "Signup failed: ${it.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
}
