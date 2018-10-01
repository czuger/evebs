module Assert
  def assert(result, error_msg, mod, action)
    raise "#{Time.now} - #{mod}##{action} : #{error_msg}" unless result
  end
end