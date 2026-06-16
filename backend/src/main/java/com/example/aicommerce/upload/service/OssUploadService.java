package com.example.aicommerce.upload.service;

import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import com.aliyun.oss.model.ObjectMetadata;
import com.example.aicommerce.common.BusinessException;
import com.example.aicommerce.upload.config.AliyunOssProperties;
import com.example.aicommerce.upload.dto.UploadResponse;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

@Service
public class OssUploadService {
    private static final long MAX_FILE_SIZE = 5L * 1024 * 1024;
    private static final Set<String> ALLOWED_EXTENSIONS = new HashSet<String>(Arrays.asList("jpg", "jpeg", "png", "webp"));
    private static final Set<String> ALLOWED_CONTENT_TYPES = new HashSet<String>(Arrays.asList("image/jpeg", "image/png", "image/webp"));
    private static final DateTimeFormatter PATH_DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy/MM");

    private final AliyunOssProperties properties;

    public OssUploadService(AliyunOssProperties properties) {
        this.properties = properties;
    }

    public UploadResponse uploadProductImage(MultipartFile file) {
        validateConfig();
        validateFile(file);

        String extension = getExtension(file.getOriginalFilename());
        String objectKey = "product-images/" + LocalDate.now().format(PATH_DATE_FORMATTER) + "/" + UUID.randomUUID().toString().replace("-", "") + "." + extension;

        ObjectMetadata metadata = new ObjectMetadata();
        metadata.setContentLength(file.getSize());
        metadata.setContentType(file.getContentType());

        OSS ossClient = new OSSClientBuilder().build(
                properties.getEndpoint(),
                properties.getAccessKeyId(),
                properties.getAccessKeySecret()
        );
        try {
            ossClient.putObject(properties.getBucketName(), objectKey, file.getInputStream(), metadata);
        } catch (IOException exception) {
            throw new BusinessException(500, "读取上传文件失败");
        } catch (RuntimeException exception) {
            throw new BusinessException(500, "上传到阿里云 OSS 失败：" + exception.getMessage());
        } finally {
            ossClient.shutdown();
        }

        return new UploadResponse(buildPublicUrl(objectKey), objectKey);
    }

    private void validateConfig() {
        if (!StringUtils.hasText(properties.getEndpoint())
                || !StringUtils.hasText(properties.getBucketName())
                || !StringUtils.hasText(properties.getAccessKeyId())
                || !StringUtils.hasText(properties.getAccessKeySecret())) {
            throw new BusinessException(500, "阿里云 OSS 未配置，请设置 ALIYUN_OSS_ENDPOINT、ALIYUN_OSS_BUCKET、ALIYUN_OSS_ACCESS_KEY_ID 和 ALIYUN_OSS_ACCESS_KEY_SECRET");
        }
    }

    private void validateFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException("请选择要上传的图片");
        }
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new BusinessException("图片大小不能超过 5MB");
        }

        String extension = getExtension(file.getOriginalFilename());
        if (!ALLOWED_EXTENSIONS.contains(extension)) {
            throw new BusinessException("仅支持 jpg、jpeg、png、webp 图片");
        }

        String contentType = file.getContentType();
        if (!StringUtils.hasText(contentType) || !ALLOWED_CONTENT_TYPES.contains(contentType.toLowerCase(Locale.ROOT))) {
            throw new BusinessException("图片类型不正确");
        }
    }

    private String getExtension(String filename) {
        if (!StringUtils.hasText(filename) || !filename.contains(".")) {
            throw new BusinessException("无法识别图片格式");
        }
        return filename.substring(filename.lastIndexOf('.') + 1).toLowerCase(Locale.ROOT);
    }

    private String buildPublicUrl(String objectKey) {
        if (StringUtils.hasText(properties.getPublicBaseUrl())) {
            return trimTrailingSlash(properties.getPublicBaseUrl()) + "/" + objectKey;
        }
        String endpoint = properties.getEndpoint();
        String normalizedEndpoint = endpoint.startsWith("http://") || endpoint.startsWith("https://")
                ? endpoint
                : "https://" + endpoint;
        return normalizedEndpoint.replace("://", "://" + properties.getBucketName() + ".") + "/" + objectKey;
    }

    private String trimTrailingSlash(String value) {
        String result = value;
        while (result.endsWith("/")) {
            result = result.substring(0, result.length() - 1);
        }
        return result;
    }
}
