package com.nithin.healthapp.util

import java.text.SimpleDateFormat
import java.util.*

object DateUtils {
    private val apiFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
    private val displayDateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
    private val displayTimeFormat = SimpleDateFormat("hh:mm a", Locale.getDefault())
    private val displayDateTimeFormat = SimpleDateFormat("MMM dd, yyyy • hh:mm a", Locale.getDefault())
    private val inputFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

    fun formatForApi(year: Int, month: Int, day: Int, hour: Int, minute: Int): String {
        val cal = Calendar.getInstance()
        cal.set(year, month, day, hour, minute, 0)
        return apiFormat.format(cal.time)
    }

    fun formatDisplayDate(dateString: String): String {
        return try {
            val date = inputFormat.parse(dateString)
            displayDateFormat.format(date!!)
        } catch (e: Exception) {
            dateString.substringBefore("T")
        }
    }

    fun formatDisplayTime(dateString: String): String {
        return try {
            val date = inputFormat.parse(dateString)
            displayTimeFormat.format(date!!)
        } catch (e: Exception) {
            ""
        }
    }

    fun formatDisplayDateTime(dateString: String): String {
        return try {
            val date = inputFormat.parse(dateString)
            displayDateTimeFormat.format(date!!)
        } catch (e: Exception) {
            dateString
        }
    }

    fun getStatusColor(status: String): Int {
        return when (status.lowercase()) {
            "SCHEDULED" -> android.graphics.Color.parseColor("#2196F3")
            "CONFIRMED" -> android.graphics.Color.parseColor("#4CAF50")
            "CANCELLED" -> android.graphics.Color.parseColor("#F44336")
            "COMPLETED" -> android.graphics.Color.parseColor("#9E9E9E")
            else -> android.graphics.Color.parseColor("#757575")
        }
    }

    fun getUrgencyColor(urgency: String): Int {
        return when (urgency.lowercase()) {
            "HIGH" -> android.graphics.Color.parseColor("#F44336")
            "MEDIUM" -> android.graphics.Color.parseColor("#FF9800")
            "LOW" -> android.graphics.Color.parseColor("#4CAF50")
            else -> android.graphics.Color.parseColor("#757575")
        }
    }
}
