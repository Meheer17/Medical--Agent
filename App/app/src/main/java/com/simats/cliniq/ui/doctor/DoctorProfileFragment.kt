package com.simats.cliniq.ui.doctor

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import com.simats.cliniq.data.local.SessionManager
import com.simats.cliniq.databinding.FragmentDoctorProfileBinding

class DoctorProfileFragment : Fragment() {

    private var _binding: FragmentDoctorProfileBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDoctorProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val user = SessionManager.getInstance(requireContext()).getUser()
        binding.tvName.text = user?.fullName ?: user?.username ?: "Doctor"
        binding.tvEmail.text = user?.email ?: ""
        binding.tvUsername.text = "Username: ${user?.username}"

        binding.btnCopyCode.setOnClickListener {
            val code = binding.tvDoctorCode.text.toString()
            if (code.isNotEmpty() && code != "Loading...") {
                val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                clipboard.setPrimaryClip(ClipData.newPlainText("Doctor Code", code))
                Toast.makeText(requireContext(), "Code copied!", Toast.LENGTH_SHORT).show()
            }
        }

        binding.btnRegenerateCode.setOnClickListener {
            viewModel.regenerateCode()
        }

        viewModel.doctorCode.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                binding.tvDoctorCode.text = it.doctorCode
                binding.tvCodeMessage.text = it.message
            }
            result.onFailure {
                binding.tvDoctorCode.text = "Error loading code"
            }
        }

        viewModel.patients.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                binding.tvPatientCount.text = "${it.patientCount} patients linked"
            }
        }

        viewModel.loadDoctorCode()
        viewModel.loadPatients()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
