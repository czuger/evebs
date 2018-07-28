module Modules::Nvl

  # If a number does not exist : then assigns it to minus infinity
  def nvl( number, null_value = -Float::INFINITY )
    number ? number : null_value
  end

end