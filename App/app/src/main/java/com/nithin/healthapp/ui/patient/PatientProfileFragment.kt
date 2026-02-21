package com.nithin.healthapp.ui.patient

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.nithin.healthapp.R
import com.nithin.healthapp.data.models.PatientProfileUpdate
import com.nithin.healthapp.databinding.FragmentPatientProfileBinding

class PatientProfileFragment : Fragment() {

    private var _binding: FragmentPatientProfileBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentPatientProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.swipeRefresh.setOnRefreshListener { viewModel.loadProfile() }

        binding.btnSaveProfile.setOnClickListener { saveProfile() }
        binding.btnLinkDoctor.setOnClickListener { showLinkDoctorDialog() }
        binding.btnUnlinkDoctor.setOnClickListener { unlinkDoctor() }

        viewModel.profile.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { profile ->
                binding.etFullName.setText(profile.fullName ?: "")
                binding.etEmail.setText(profile.email)
                binding.etPhone.setText(profile.phone ?: "")
                binding.etAddress.setText(profile.address ?: "")
                binding.tvUsername.text = "Username: ${profile.username}"

                if (profile.linkedDoctorId != null) {
                    binding.cardLinkedDoctor.visibility = View.VISIBLE
                    binding.btnLinkDoctor.visibility = View.GONE
                    viewModel.loadLinkedDoctor()
                } else {
                    binding.cardLinkedDoctor.visibility = View.GONE
                    binding.btnLinkDoctor.visibility = View.VISIBLE
                }
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error loading profile", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.linkedDoctor.observe(viewLifecycleOwner) { result ->
            result.onSuccess { doctor ->
                binding.tvDoctorName.text = doctor.name
                binding.tvDoctorEmail.text = doctor.email
                binding.tvDoctorPhone.text = doctor.phone ?: "No phone"
            }
        }

        viewModel.profileUpdate.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Profile updated!", Toast.LENGTH_SHORT).show()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Update failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.linkResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Linked to doctor!", Toast.LENGTH_SHORT).show()
                viewModel.loadProfile()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Link failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loadProfile()
    }

    private fun saveProfile() {
        val update = PatientProfileUpdate(
            fullName = binding.etFullName.text?.toString()?.trim(),
            phone = binding.etPhone.text?.toString()?.trim(),
            address = binding.etAddress.text?.toString()?.trim()
        )
        viewModel.updateProfile(update)
    }

    private fun showLinkDoctorDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_link_doctor, null)
        val etCode = dialogView.findViewById<TextInputEditText>(R.id.et_doctor_code)

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Link to Doctor")
            .setMessage("Enter the doctor's unique code")
            .setView(dialogView)
            .setPositiveButton("Link") { _, _ ->
                val code = etCode.text?.toString()?.trim()
                if (code.isNullOrEmpty()) {
                    Toast.makeText(requireContext(), "Please enter a code", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.linkToDoctor(code)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun unlinkDoctor() {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Unlink Doctor")
            .setMessage("Are you sure you want to unlink from your doctor?")
            .setPositiveButton("Unlink") { _, _ -> viewModel.unlinkDoctor() }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
