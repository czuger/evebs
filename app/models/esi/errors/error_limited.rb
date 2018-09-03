module Esi::Errors
  class ErrorLimited < Base

    def error_hook
      exit
    end

  end
end
