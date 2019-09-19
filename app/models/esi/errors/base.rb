require 'pp'

class Esi::Errors::Base < RuntimeError

  def self.dispatch( exception )

    # return Esi::Errors::SocketError.new if exception.message =~ /SocketError/

    case exception.message

      when '500 Internal Server Error'
        error = Esi::Errors::GatewayTimeout.new
      when '504 Gateway Timeout', '504 Gateway Time-out'
        error = Esi::Errors::GatewayTimeout.new
      when '502 Bad Gateway'
        error = Esi::Errors::BadGateway.new
      when '403 Forbidden'
        error = Esi::Errors::Forbidden.new
      when '420 status code 420'
        error = Esi::Errors::ErrorLimited.new
      when '404 Not Found'
        error = Esi::Errors::NotFound.new
      when 'Net::OpenTimeout'
        error = Esi::Errors::OpenTimeout.new
      when 'SocketError'
        error = Esi::Errors::SocketError.new
      when '503 Service Unavailable'
        error = Esi::Errors::ServiceUnavailable.new
      when '520 status code 520'
        error = Esi::Errors::UnknownError.new
			else
				pp exception
        raise 'Unhandled error'
      end

    error
  end

  def retry?
    false
  end

end